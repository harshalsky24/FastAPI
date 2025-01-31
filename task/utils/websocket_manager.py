from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List

class WebSocketManager:
    """
        Manages WebSocket connections for real-time communication.
    """
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        """Accept WebSocket connection and store it for a user."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"WebSocket connected for user {user_id}. Active Users: {list(self.active_connections.keys())}")

    async def disconnect(self, user_id: int):
        """Remove WebSocket connection when the user disconnects."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"WebSocket disconnected for user {user_id}.")

    async def send_personal_message(self, user_id: int, message: str):
        """Send message to a specific user if connected."""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
                print(f"Sent message to user {user_id}: {message}")
            except Exception as e:
                print(f"Error sending message to {user_id}: {str(e)}")
        else:
            print(f"User {user_id} is not connected.")

    async def broadcast_to_team(self, user_ids: List[int], message: str):
        """Send message to multiple users."""
        print(f"Broadcasting message: '{message}' to users: {user_ids}")
        for user_id in user_ids:
            await self.send_personal_message(user_id, message)

manager = WebSocketManager()
