# myapp/models/__init__.py

# Baseの統一
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # プロジェクト全体で共通のBaseを使用

from models.chapter_model import ChapterModel
from models.chapter_history_model import ChapterHistoryModel
from models.novel_model import NovelModel
from models.novel_tag_model import NovelTagModel
from models.scrape_log_model import ScrapeLogModel
from models.tag_model import TagModel