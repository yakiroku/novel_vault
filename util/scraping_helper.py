class ScrapingHelper:
    @staticmethod
    def get_first_value(value: str | list[str] | None) -> str | None:
        if isinstance(value, list):
            return value[0] if value else None
        return value
