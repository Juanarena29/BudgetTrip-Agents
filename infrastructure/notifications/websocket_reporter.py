from fastapi import WebSocket

from budgettrip.application.ports.progress_port import ProgressReporter


class WebSocketReporter(ProgressReporter):
    def __init__(self, websocket: WebSocket) -> None:
        self.websocket = websocket

    async def report(self, message: str) -> None:
        await self.websocket.send_json({"status": message})
