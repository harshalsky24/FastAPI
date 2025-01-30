from fastapi import WebSocket
from typing import Dict, List

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        """Connect a user to WebSocket and store their connection."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        print(f"User {user_id} connected to WebSocket.")

    def disconnect(self, user_id: int, websocket: WebSocket):
        """Disconnect a user's WebSocket connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:  # Remove empty list
                del self.active_connections[user_id]
        print(f"User {user_id} disconnected.")

    async def send_personal_message(self, user_id: int, message: str):
        """Send a notification to a specific user."""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_text(message)

    async def broadcast_to_team(self, user_ids: List[int], message: str):
        """Broadcast a message to multiple users."""
        for user_id in user_ids:
            await self.send_personal_message(user_id, message)

# Create a WebSocket manager instance
manager = WebSocketManager()
