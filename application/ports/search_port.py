from typing import Protocol

from budgettrip.domain.entities import SearchItem


class SearchProvider(Protocol):
    async def search(self, item: SearchItem) -> str: ...
