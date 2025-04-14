from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from task.utils.websocket_manager import manager
from task.auth import get_current_user
from task.auth import verify_jwt_token

router = APIRouter()
active_connections = {} #connection alive

@router.websocket("/ws/notifications/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """
        WebSocket endpoint for real-time notifications.

        This endpoint establishes a WebSocket connection for a given user, allowing 
        real-time message exchange between the client and the server.
    
        Functionality:
            Connects the user to the WebSocket manager.
            Listens for incoming messages from the user.
            Sends acknowledgment messages back to the client.
            Handles disconnection when the user disconnects.
    """
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        manager.disconnect(user_id)