import re
from typing import Any
from flask import Flask, redirect, request, render_template
from sqlalchemy import and_, distinct, func, select, desc, asc
from math import ceil
from db.db_session_manager import DBSessionManager
from models import ChapterModel
from models.novel_model import NovelModel
from models.novel_tag_model import NovelTagModel
from models.paragraph_model import ParagraphModel
from models.tag_model import TagModel
from repositories.services.chapter_service import ChapterService
# from repositories.services.novel_favorite_service import NovelFavoriteService
from repositories.services.novel_service import NovelService

# Flask アプリケーションの初期化a
app = Flask(__name__)

# 1ページに表示する結果数
RESULTS_PER_PAGE = 50


@app.route("/", methods=["GET", "POST"])
@app.route("/search", methods=["GET", "POST"])
def search():
    keyword = request.values.get("q", "").strip()
    sort_order = request.values.get("sort", "desc")
    page = int(request.values.get("page", 1))
    novel_id_filter = request.values.get("novel_id")

    search_results = []
    total_pages = 0

    if keyword:
        with DBSessionManager.session() as session:
            # --- タグ絞り込み用の設定 ---
            tag_names = ["NTR", "寝取られ"]
            # 1. ページネーション用の「総件数」を取得 (count)
            # 巨大なデータを取得しないので、ここは軽量です
            count_stmt = (
                select(func.count(distinct(ChapterModel.id)))
                .join(NovelModel, NovelModel.id == ChapterModel.novel_id)
                .join(ParagraphModel, ParagraphModel.chapter_id == ChapterModel.id)
                .join(NovelTagModel, NovelTagModel.novel_id == NovelModel.id) # タグ接続用
                .join(TagModel, TagModel.id == NovelTagModel.tag_id)           # タグ接続用
                .filter(
                    and_(
                        NovelModel.excluded == False,
                        ParagraphModel.content.like(f"%{keyword}%"),
                        # TagModel.name.in_(tag_names)  # タグで絞り込み
                    )
                )
            )
            if novel_id_filter:
                count_stmt = count_stmt.filter(ChapterModel.novel_id == int(novel_id_filter))
            
            total_results = session.execute(count_stmt).scalar()
            total_pages = ceil(total_results / RESULTS_PER_PAGE) # type: ignore

            # 2. 現在のページに必要な「Chapter.id」だけを取得 (LIMIT / OFFSET)
            # ここでDB側にページネーションを任せるのが最大のポイントです
# 2. 現在のページに必要な「Chapter.id」だけを取得 (LIMIT / OFFSET)
            match sort_order:
                case "desc": 
                    order_by = desc(ChapterModel.posted_at)
                    sort_col = ChapterModel.posted_at # SELECTに追加するため
                case "asc": 
                    order_by = asc(ChapterModel.posted_at)
                    sort_col = ChapterModel.posted_at
                case "id_asc": 
                    order_by = asc(ChapterModel.novel_id)
                    sort_col = ChapterModel.novel_id
                case "random": 
                    order_by = func.random()
                    sort_col = None
                case _:
                    order_by = desc(ChapterModel.posted_at)
                    sort_col = ChapterModel.posted_at

            offset_val = (page - 1) * RESULTS_PER_PAGE
            
            # --- 修正箇所 ---
            # select に ChapterModel.id だけでなく sort_col も含める
            columns_to_select: list[Any] = [ChapterModel.id]
            if sort_col is not None:
                columns_to_select.append(sort_col)

            id_stmt = (
                select(*columns_to_select)
                .distinct()
                .join(NovelModel, NovelModel.id == ChapterModel.novel_id)
                .join(ParagraphModel, ParagraphModel.chapter_id == ChapterModel.id)
                .join(NovelTagModel, NovelTagModel.novel_id == NovelModel.id) # タグ接続
                .join(TagModel, TagModel.id == NovelTagModel.tag_id)           # タグ接続
                .filter(
                    and_(
                        NovelModel.excluded == False,
                        ParagraphModel.content.like(f"%{keyword}%"),
                        # TagModel.name.in_(tag_names)  # タグで絞り込み
                    )
                )
                .order_by(order_by)
                .limit(RESULTS_PER_PAGE)
                .offset(offset_val)
            )
            if novel_id_filter:
                id_stmt = id_stmt.filter(ChapterModel.novel_id == int(novel_id_filter))

            # 取得時は ID だけが必要なので、r[0] で ID を取り出す（変更なし）
            target_ids = [r[0] for r in session.execute(id_stmt).all()]

            if target_ids:
                # 3. 確定した50件分の詳細データ（本文含む）のみを取得
                # target_ids に絞ることで、DBから転送されるデータ量を劇的に減らせます
                detail_stmt = (
                    select(ChapterModel, ParagraphModel, NovelModel)
                    .join(NovelModel, NovelModel.id == ChapterModel.novel_id)
                    .join(ParagraphModel, ParagraphModel.chapter_id == ChapterModel.id)
                    .filter(ChapterModel.id.in_(target_ids))
                    # 検索ワードにヒットした段落だけを連れてくる
                    .filter(ParagraphModel.content.like(f"%{keyword}%"))
                    .order_by(order_by, asc(ParagraphModel.id))
                )
                
                detail_results = session.execute(detail_stmt).all()

                # タグ情報の取得 (対象のNovel IDに限定)
                target_novel_ids = {novel.id for _, _, novel in detail_results}
                tag_stmt = (
                    select(NovelTagModel.novel_id, TagModel.name)
                    .join(TagModel, TagModel.id == NovelTagModel.tag_id)
                    .filter(NovelTagModel.novel_id.in_(target_novel_ids))
                )
                tags_results = session.execute(tag_stmt).fetchall()
                
                tags_by_novel = {}
                for n_id, t_name in tags_results:
                    tags_by_novel.setdefault(n_id, set()).add(t_name)

                # 4. データのグルーピング
                grouped_results = {}
                for chapter, paragraph, novel in detail_results:
                    if chapter.id not in grouped_results:
                        grouped_results[chapter.id] = {
                            "chapter": chapter,
                            "novel": novel,
                            "tags": tags_by_novel.get(novel.id, set()),
                            "paragraphs": [],
                        }
                    grouped_results[chapter.id]["paragraphs"].append({"content": paragraph.content})

                # 5. フロントエンド用データの整形 (サマリー抽出)
                for res in grouped_results.values():
                    chapter = res["chapter"]
                    novel = res["novel"]
                    
                    # 各段落からキーワード周辺を切り出し
                    for p in res["paragraphs"]:
                        content = p["content"]
                        idx = content.lower().find(keyword.lower())
                        if idx != -1:
                            start = max(idx - 30, 0)
                            end = min(idx + len(keyword) + 200, len(content))
                            p["content"] = content[start:end].replace("\n", " ").strip()
                        else:
                            p["content"] = content[:200] # 万が一見つからない場合

                    search_results.append({
                        "novel_id": novel.id,
                        "title": novel.title,
                        "author": novel.author,
                        "tags": ", ".join(res["tags"]),
                        "chapter": chapter.title,
                        "paragraphs": res["paragraphs"],
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
        novel_id=novel_id_filter,
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

# @app.route("/novel_favorites", methods=["POST"])
# def novel_favorites():
#     novel_id = request.form.get("novel_id")
#     tags = request.form.get("tags")
#     if novel_id is not None:
#         with DBSessionManager.auto_commit_session() as session:
#             novel_favorite_service = NovelFavoriteService(session)
#             novel_favorite_service.favorite(int(novel_id), tags)

#     # 元の検索結果ページにリダイレクト
#     return redirect(request.referrer)

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
        if chapter is not None and chapter.paragraphs is not None:
            chapter.content = break_text_by_punctuation(chapter.paragraphs)
        # app.logger.debug(chapter.content)

    # 取得した章をテンプレートに渡して表示
    return render_template("chapter.html", chapter=chapter)

@app.route("/excluded_novels")
def excluded_novels():
    """
    除外された小説一覧を表示する
    """
    with DBSessionManager.session() as session:
        novel_service = NovelService(session)
        novels = novel_service.excluded_novels()
    return render_template("excluded_novels.html", novels=novels)

def break_text_by_punctuation(paragraphs: list[ParagraphModel]) -> str:
    text = ""
    for paragraph in paragraphs:
        # 句読点（。や、）で文章を区切り、改行を挿入する
        # ここでは「。」や「,」の後に改行を挿入する
        text += re.sub(r"([。」])", r"\1\n", paragraph.content)
    return text


if __name__ == "__main__":
    app.run(debug=True)
