from search.nocturne_ranked_search import NocturneRankedSearch
from search.nocturne_tag_search import NocturneTagSearch
from search.nocturne_tag_weekly_search import NocturneTagWeeklySearch
from search.pixiv_tag_search import PixivTagSearch
from shared.enums.search_target import SearchTarget


class NovelSearchFactory:
    """ 
    小説検索ファクトリークラス
    """

    @staticmethod
    def create_searcher(target: SearchTarget):
        """
        検索対象を生成する

        Args:
            target (SearchTarget): 検索対象
        """
        match target:
            case SearchTarget.NOCTURNE_RANKED:
                return NocturneRankedSearch()
            case SearchTarget.NOCTURNE_TAG:
                return NocturneTagSearch()
            case SearchTarget.NOCTURNE_WEEKLY_TAG:
                return NocturneTagWeeklySearch()
            case SearchTarget.PIXIV_TAG:
                return PixivTagSearch()
            case _:
                raise ValueError(f"Unsupported search target: {target}")
