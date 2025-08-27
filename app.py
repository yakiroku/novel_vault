import re
from flask import Flask, redirect, request, render_template
from sqlalchemy import and_, func, select, desc, asc
from math import ceil
from db.db_session_manager import DBSessionManager
from models import ChapterModel
from models.novel_model import NovelModel
from models.novel_tag_model import NovelTagModel
from models.paragraph_model import ParagraphModel
from models.tag_model import TagModel
from repositories.services.chapter_service import ChapterService
from repositories.services.novel_service import NovelService

# Flask アプリケーションの初期化
app = Flask(__name__)

# 1ページに表示する結果数
RESULTS_PER_PAGE = 50


@app.route("/", methods=["GET", "POST"])
@app.route("/search", methods=["GET", "POST"])
def search():
    # 検索キーワードを取得（POST/GET のどちらにも対応）
    keyword = request.values.get("q", "").strip()
    sort_order = request.values.get("sort", "desc")  # デフォルトは降順
    page = int(request.values.get("page", 1))  # 現在のページ（デフォルトは1）
    novel_id = request.values.get("novel_id")  # 小説IDで絞り込む

    # デフォルトの検索結果
    search_results = []
    total_pages = 0

    if keyword:
        with DBSessionManager.session() as session:
            # ソート順を設定
            match sort_order:
                case "desc":
                    order_by = desc(ChapterModel.posted_at)
                case "asc":
                    order_by = asc(ChapterModel.posted_at)
                case "id_asc":
                    order_by = asc(ChapterModel.novel_id)
                case "random":  # ランダム順を追加
                    order_by = func.random()
                case _:
                    # デフォルトのソート順を設定
                    order_by = desc(ChapterModel.posted_at)

            tag_names = ["NTR","寝取られ"]
            # クエリのベース
            stmt = (
                select(
                    ChapterModel,
                    ParagraphModel,
                    NovelModel,
                )
                .join(NovelModel, NovelModel.id == ChapterModel.novel_id)
                .outerjoin(ParagraphModel, ParagraphModel.chapter_id == ChapterModel.id)
                .join(NovelTagModel, NovelTagModel.novel_id == NovelModel.id)
                # .outerjoin(TagModel, TagModel.id == NovelTagModel.tag_id)
                .filter(
                       and_(
                        NovelModel.excluded == False,
                        ParagraphModel.content.like(f"%{keyword}%"),
                        TagModel.name.in_(tag_names)
                    )
                )
                .distinct()
            )

            # 小説IDで絞り込む場合
            if novel_id:
                stmt = stmt.filter(ChapterModel.novel_id == int(novel_id))
                # 並び順を設定
                stmt = stmt.order_by(asc(ChapterModel.created_at), asc(ParagraphModel.id))
            else:
                # 並び順を設定
                stmt = stmt.order_by(order_by, asc(ParagraphModel.id))

            # メインクエリ実行
            results = session.execute(stmt).all()

            # メインクエリからNovelModelのIDを抽出
            novel_ids = {novel.id for _, _, novel in results}

            # タグを取得するクエリ
            tag_stmt = (
                select(NovelTagModel.novel_id, TagModel.name.label("tag_name"))
                .join(TagModel, TagModel.id == NovelTagModel.tag_id)
                .filter(NovelTagModel.novel_id.in_(novel_ids))
            )

            # タグを取得
            tags_results = session.execute(tag_stmt).fetchall()

            # タグをnovel_idごとにまとめる
            tags_by_novel = {}
            for novel_id, tag_name in tags_results:
                if novel_id not in tags_by_novel:
                    tags_by_novel[novel_id] = set()
                tags_by_novel[novel_id].add(tag_name)

            # データをグループ化してタグをまとめる
            grouped_results = {}
            for chapter, paragraph, novel in results:
                if chapter.id not in grouped_results:
                    grouped_results[chapter.id] = {
                        "chapter": chapter,
                        "novel": novel,
                        "tags": set(),
                        "paragraphs": [],
                    }

                # paragraphをchapterごとに追加
                grouped_results[chapter.id]["paragraphs"].append(
                    {
                        "content": paragraph.content,
                    }
                )

                # タグを追加
                if novel.id in tags_by_novel:
                    grouped_results[chapter.id]["tags"].update(tags_by_novel[novel.id])

            # ページング処理
            total_results = len(grouped_results)
            total_pages = ceil(total_results / RESULTS_PER_PAGE)
            start = (page - 1) * RESULTS_PER_PAGE
            end = start + RESULTS_PER_PAGE
            paginated_results = list(grouped_results.values())[start:end]

            # 検索結果の整形
            for result in paginated_results:
                paragraphs = result["paragraphs"]
                chapter = result["chapter"]
                novel = result["novel"]
                tags = ", ".join(result["tags"])

                for paragraph in paragraphs:
                    content = paragraph["content"]
                    idx = content.lower().find(keyword.lower())
                    summary_start = max(idx - 30, 0)
                    summary_end = min(idx + len(keyword) + 200, len(content))
                    paragraph["content"] = (
                        content[summary_start:summary_end].replace("\n", " ").strip()
                    )

                search_results.append(
                    {
                        "novel_id": chapter.novel_id,
                        "title": novel.title,
                        "author": novel.author,
                        "tags": tags,
                        "chapter": chapter.title,
                        "paragraphs": paragraphs,
                        "source_url": chapter.source_url,
                        "id": chapter.id,
                        "posted_at": chapter.posted_at.strftime("%Y-%m-%d %H:%M"),
                    }
                )

    # 検索結果を表示
    return render_template(
        "search.html",
        results=search_results,
        keyword=keyword,
        sort_order=sort_order,
        current_page=page,
        total_pages=total_pages,
        novel_id=novel_id,  # フロントで使用するため渡す
    )


@app.route("/exclude", methods=["POST"])
def exclude_novel():
    novel_id = request.form.get("novel_id")
    if novel_id is not None:
        with DBSessionManager.auto_commit_session() as session:
            novel_service = NovelService(session)
            novel_service.exclude_novel(int(novel_id))

    # 元の検索結果ページにリダイレクト
    return redirect(request.referrer)


@app.route("/chapter/<int:id>", methods=["GET"])
def show_chapter(id):
    app.logger.debug("chapter")
    # Chapterのデータをデータベースから取得
    with DBSessionManager.session() as session:
        chapter_service = ChapterService(session)
        chapter = chapter_service.get_by_id(id)

    # 該当の章が見つからない場合は404エラーを返す
    # if chapter is None:
    #     abort(404)
    if chapter is not None and chapter.content is not None:
        chapter.content = break_text_by_punctuation(chapter.content)
        # app.logger.debug(chapter.content)

    # 取得した章をテンプレートに渡して表示
    return render_template("chapter.html", chapter=chapter)


def break_text_by_punctuation(text: str) -> str:
    # 句読点（。や、）で文章を区切り、改行を挿入する
    # ここでは「。」や「,」の後に改行を挿入する
    text = re.sub(r"([。」])", r"\1\n", text)
    return text


if __name__ == "__main__":
    app.run(debug=True)
