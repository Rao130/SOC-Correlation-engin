import asyncio
import logging
from typing import Dict, Any

class WebSocketManager:
    """Simple WebSocket manager for demo purposes"""
    
    def __init__(self):
        self.active_connections = []
        self.connected = False
    
    async def connect(self, websocket):
        """Accept a WebSocket connection"""
        self.active_connections.append(websocket)
        self.connected = True
        logging.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    async def disconnect(self, websocket):
        """Handle a WebSocket disconnection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        self.connected = len(self.active_connections) > 0
        logging.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def handle_message(self, websocket, message: str):
        """Handle incoming WebSocket message"""
        try:
            data = {"type": "message", "content": message}
            await self.broadcast(data)
        except Exception as e:
            logging.error(f"Error handling WebSocket message: {e}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        if self.active_connections:
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logging.error(f"Error sending WebSocket message: {e}")
    
    def is_connected(self) -> bool:
        """Check if any clients are connected"""
        return self.connected
