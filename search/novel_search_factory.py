from search.nocturne_ranked_search import NocturneRankedSearch
from search.nocturne_tag_search import NocturneTagSearch
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
            case _:
                raise ValueError(f"Unsupported search target: {target}")
