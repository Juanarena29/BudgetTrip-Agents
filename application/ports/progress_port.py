from typing import Protocol


class ProgressReporter(Protocol):
    async def report(self, message: str) -> None: ...


class NoOpReporter:
    async def report(self, message: str) -> None:
        pass
