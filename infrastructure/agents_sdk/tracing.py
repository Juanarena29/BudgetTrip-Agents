import contextlib

from agents import trace as openai_trace

from budgettrip.application.ports.tracing_port import TracingProvider


class OpenAITracingProvider(TracingProvider):
    def trace(self, name: str) -> contextlib.AbstractContextManager[None]:
        return openai_trace(name)
