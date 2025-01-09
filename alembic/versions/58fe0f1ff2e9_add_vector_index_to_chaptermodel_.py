"""Add vector index to ChapterModel.embedding

Revision ID: 58fe0f1ff2e9
Revises: ac6ca6a6ec8e
Create Date: 2025-01-09 16:20:47.397341

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import tidb_vector
from tidb_vector.sqlalchemy import VectorAdaptor

from db.db_session_manager import DBSessionManager
from models.paragraph_model import ParagraphModel

# revision identifiers, used by Alembic.
revision: str = "58fe0f1ff2e9"
down_revision: Union[str, None] = "ac6ca6a6ec8e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ベクトルインデックスを作成
    VectorAdaptor(DBSessionManager.engine()).create_vector_index(
        ParagraphModel.embedding,  # テーブル名とカラム名を指定 # type: ignore
        tidb_vector.DistanceMetric.L2,  # L2距離を使用
        skip_existing=True,
    )


def downgrade() -> None:
    pass
