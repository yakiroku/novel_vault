import logging
import re
from flask import Flask, abort, redirect, request, render_template
from sqlalchemy import and_, create_engine, select, text, desc, asc
from sqlalchemy.orm import sessionmaker, scoped_session
from math import ceil
from db.db_session_manager import DBSessionManager
from models import ChapterModel
from models.novel_model import NovelModel
from models.novel_tag_model import NovelTagModel
from models.tag_model import TagModel
from repositories.services.chapter_service import ChapterService
from repositories.services.novel_service import NovelService  # モデルのインポート

# Flask アプリケーションの初期化
app = Flask(__name__)

# 1ページに表示する結果数
RESULTS_PER_PAGE = 50

@app.route("/", methods=["GET", "POST"])
def search():
    # 検索キーワードを取得（POST/GET のどちらにも対応）
    keyword = request.values.get("q", "").strip()
    sort_order = request.values.get("sort", "desc")  # デフォルトは降順
    page = int(request.values.get("page", 1))  # 現在のページ（デフォルトは1）

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
                case _:
                    # デフォルトのソート順を設定
                    order_by = desc(ChapterModel.posted_at)

            # pgroongaを使用した全文検索
            stmt = (
                select(
                    ChapterModel,
                    NovelModel,
                    TagModel.name.label("tag_name")  # タグ名を取得
                )
                .join(NovelModel, NovelModel.id == ChapterModel.novel_id)  # ChapterModelとNovelModelを結合
                .outerjoin(NovelTagModel, NovelTagModel.novel_id == NovelModel.id)  # 中間テーブルを結合
                .outerjoin(TagModel, TagModel.id == NovelTagModel.tag_id)  # TagModelと結合
                .where(
                    and_(
                        text("chapters.content @@ :keyword"),  # pgroonga全文検索条件
                        NovelModel.excluded == False,  # 除外されていない条件
                    )
                )
                .order_by(order_by)  # 並び順を設定
            )

            # クエリ実行
            results = session.execute(stmt, {"keyword": keyword}).all()

            # データをグループ化してタグをまとめる
            grouped_results = {}
            for chapter, novel, tag_name in results:
                if chapter.id not in grouped_results:
                    grouped_results[chapter.id] = {
                        "chapter": chapter,
                        "novel": novel,
                        "tags": set(),
                    }
                if tag_name:
                    grouped_results[chapter.id]["tags"].add(tag_name)

            # ページング処理
            total_results = len(grouped_results)
            total_pages = ceil(total_results / RESULTS_PER_PAGE)
            start = (page - 1) * RESULTS_PER_PAGE
            end = start + RESULTS_PER_PAGE
            paginated_results = list(grouped_results.values())[start:end]

            # 検索結果の整形
            for result in paginated_results:
                chapter = result["chapter"]
                novel = result["novel"]
                tags = ", ".join(result["tags"])  # タグを文字列に結合

                # キーワードの前後 200 文字を抜き出して概要を作成
                content = chapter.content
                idx = content.lower().find(keyword.lower())
                summary_start = max(idx - 30, 0)
                summary_end = min(idx + len(keyword) + 300, len(content))
                summary = content[summary_start:summary_end].replace("\n", " ").strip()

                # 整形されたデータをリストに追加
                search_results.append({
                    "novel_id": chapter.novel_id,
                    "title": novel.title,
                    "author": novel.author,
                    "tags": tags,
                    "chapter": chapter.title,
                    "summary": summary,
                    "source_url": chapter.source_url,
                    "id": chapter.id,
                    "posted_at": chapter.posted_at.strftime("%Y-%m-%d %H:%M"),
                })

    return render_template(
        "search.html",
        results=search_results,
        keyword=keyword,
        sort_order=sort_order,
        current_page=page,
        total_pages=total_pages,
    )

@app.route('/exclude', methods=['POST'])
def exclude_novel():
    novel_id = request.form.get('novel_id')
    if novel_id is not None:
        with DBSessionManager.auto_commit_session() as session:
            novel_service = NovelService(session)
            novel_service.exclude_novel(int(novel_id))

    # 元の検索結果ページにリダイレクト
    return redirect(request.referrer)


@app.route('/chapter/<int:id>', methods=['GET'])
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
    return render_template('chapter.html', chapter=chapter)
    
def break_text_by_punctuation(text: str) -> str:
    # 句読点（。や、）で文章を区切り、改行を挿入する
    # ここでは「。」や「,」の後に改行を挿入する
    text = re.sub(r'([。」])', r'\1\n', text)
    return text


if __name__ == "__main__":
    app.run(debug=True)
