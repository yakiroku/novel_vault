from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from util.env_config_loader import EnvConfigLoader


class DBSessionManager:
    """SQLAlchemyセッションの管理を行うクラス"""

    @staticmethod
    def create_url() -> str:
        """データベース接続用のURLを作成するメソッド"""
        db_user = EnvConfigLoader.get_variable("TIDB_DB_USER")
        db_pass = EnvConfigLoader.get_variable("TIDB_DB_PASS")
        db_host = EnvConfigLoader.get_variable("TIDB_DB_HOST")
        db_port = EnvConfigLoader.get_variable("TIDB_DB_PORT")
        db_name = EnvConfigLoader.get_variable("TIDB_DB_NAME")
        db_ca = EnvConfigLoader.get_variable("TIDB_DB_CA")
        url = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}?ssl_ca={db_ca}&ssl_verify_cert=true&ssl_verify_identity=true"
        return url

    # エンジンの作成
    _engine = create_engine(create_url(), echo=False, pool_pre_ping=True)

    # セッションの作成
    _session = sessionmaker(bind=_engine)

    @staticmethod
    def session():
        """セッションを取得するメソッド"""
        return DBSessionManager._session()

    @staticmethod
    @contextmanager
    def auto_commit_session():
        """セッションスコープを管理するコンテキストマネージャー"""
        session = DBSessionManager.session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def engine():
        """エンジンを取得するメソッド"""
        return DBSessionManager._engine