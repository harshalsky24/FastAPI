from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from task.utils.websocket_manager import manager
from task.auth import get_current_user
from task.auth import verify_jwt_token

router = APIRouter()
active_connections = {}

@router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    if not token:
        await websocket.close(code=403)
        return
    
    try:
        user_id = await verify_jwt_token(token)  # Validate token
        await websocket.accept()
        print(f"✅ WebSocket connected for user: {user_id}")

        while True:
            message = await websocket.receive_text()  # Keep connection alive
            print(f"📩 Received message: {message}")

    except WebSocketDisconnect:
        print("❌ WebSocket disconnected")