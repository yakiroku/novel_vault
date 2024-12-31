from flask import Flask, request, render_template
from sqlalchemy import create_engine, select, text, desc, asc
from sqlalchemy.orm import sessionmaker, scoped_session
from math import ceil
from db.db_session_manager import DBSessionManager
from models import ChapterModel  # モデルのインポート

# Flask アプリケーションの初期化
app = Flask(__name__)


# 1ページに表示する結果数
RESULTS_PER_PAGE = 10

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
            order_by = desc(ChapterModel.posted_at) if sort_order == "desc" else asc(ChapterModel.posted_at)

            # 検索クエリを構築
            stmt = (
                select(ChapterModel)
                .where(ChapterModel.content.like(f"%{keyword}%"))
                .order_by(order_by)
            )

            # 検索結果の総数を取得
            total_results = session.execute(stmt).scalars().all()
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
                summary_start = max(idx - 200, 0)
                summary_end = min(idx + len(keyword) + 200, len(content))
                summary = content[summary_start:summary_end].replace("\n", " ").strip()

                # 整形されたデータをリストに追加
                search_results.append({
                    "title": chapter.title,
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

if __name__ == "__main__":
    app.run(debug=True)
