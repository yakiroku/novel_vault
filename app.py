from flask import Flask, redirect, request, render_template
from sqlalchemy import and_, create_engine, select, text, desc, asc
from sqlalchemy.orm import sessionmaker, scoped_session
from math import ceil
from db.db_session_manager import DBSessionManager
from models import ChapterModel
from models.novel_model import NovelModel
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
                    # デフォルトのソート順を設定（必要に応じて変更してください）
                    order_by = desc(ChapterModel.posted_at)
            # pgroongaを使用した全文検索
            stmt = (
                select(ChapterModel, NovelModel.title, NovelModel.author)
                .join(NovelModel, NovelModel.id == ChapterModel.novel_id)
                .where(
                    and_(
                        # pgroongaの全文検索演算子（@@）を使用
                        text("chapters.content @@ :keyword"),
                        NovelModel.excluded == False,  # 除外されていないものを選択
                    )
                )
                .order_by(order_by)
            )

            # 検索結果の総数を取得
            total_results = session.execute(stmt, {"keyword": keyword}).scalars().all()
            total_pages = ceil(len(total_results) / RESULTS_PER_PAGE)

            # ページングのために指定範囲を抽出
            start = (page - 1) * RESULTS_PER_PAGE
            end = start + RESULTS_PER_PAGE
            paginated_results = total_results[start:end]

            # 検索結果の整形
            for chapter in paginated_results:
                # キーワードの前後 200 文字を抜き出して概要を作成
                content = chapter.content
                idx = content.lower().find(keyword.lower())
                summary_start = max(idx - 30, 0)
                summary_end = min(idx + len(keyword) + 300, len(content))
                summary = content[summary_start:summary_end].replace("\n", " ").strip()

                # 整形されたデータをリストに追加
                search_results.append({
                    "novel_id": chapter.novel_id,
                    "title": chapter.novel.title,
                    "author": chapter.novel.author,
                    "chapter": chapter.title,
                    "summary": summary,
                    "source_url": chapter.source_url,
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

if __name__ == "__main__":
    app.run(debug=True)
