from search.nocturne_tag_search import NocturneTagSearch
from search.novel_search_interface import NovelSearchInterface
from shared.schemas.novel_summary import NovelSummary
from util.env_config_loader import EnvConfigLoader


class NocturneTagWeeklySearch(NovelSearchInterface):

    def fetch_novel_list(self) -> list[NovelSummary]:
        """複数のタグを繰り返し処理して小説の一覧を取得する"""
        all_novels = []
        nocturne_tag_search = NocturneTagSearch()

        for tag in nocturne_tag_search.get_all_search_tags():
            # 各タグに対応するURLを生成
            url = f"{EnvConfigLoader.get_variable('NOCTURNE_TAG_SEARCH_URL')}{tag.name}&order=weekly"
            all_novels.extend(nocturne_tag_search.fetch_novels_from_url(url)) 

        return all_novels
