import contextlib
from typing import Protocol


class TracingProvider(Protocol):
    def trace(self, name: str) -> contextlib.AbstractContextManager[None]: ...


class NoOpTracer:
    def trace(self, name: str) -> contextlib.AbstractContextManager[None]:
        return contextlib.nullcontext()
