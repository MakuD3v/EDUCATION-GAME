from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
import json

from .database import engine, Base, get_db
from .routers import auth
from .lobby_system import lobby_manager, Player
from .game_engine import GameSession

# Create Tables (Async) - For Dev Only. In prod use Alembic.
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(on_startup=[init_tables])

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

@app.get("/")
async def root():
    return {"status": "online", "message": "EDU PARTY Game Server is Running! Connect using the Game Client."}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    # In real app, validate token here
    await websocket.accept()
    
    # Wait for JOIN or CREATE message
    try:
        data = await websocket.receive_text()
        msg = json.loads(data)
        cmd = msg.get("command")
        username = msg.get("username", f"Player{client_id}")
        
        player = Player(websocket, username, client_id)
        lobby = None
        
        if cmd == "CREATE":
            code = lobby_manager.create_lobby()
            lobby = lobby_manager.get_lobby(code)
            await lobby.connect(player)
            await websocket.send_json({"type": "LOBBY_CREATED", "code": code})
            
        elif cmd == "JOIN":
            code = msg.get("code")
            lobby = lobby_manager.get_lobby(code)
            if lobby:
                await lobby.connect(player)
                await websocket.send_json({"type": "LOBBY_JOINED", "code": code})
            else:
                await websocket.send_json({"type": "ERROR", "msg": "Lobby not found"})
                await websocket.close()
                return

        # Main Loop for this connection
        if lobby:
            while True:
                data = await websocket.receive_text()
                # Handle Game Inputs here
                msg = json.loads(data)
                if msg.get("command") == "GAME_INPUT":
                    # We need access to the game session. 
                    # For MVP, assume lobby has a 'game_session' attribute or we attach it.
                    # Let's make sure Lobby tracks the session.
                    if hasattr(lobby, "game_session") and lobby.game_session:
                        await lobby.game_session.handle_input(player, msg.get("input"))
                    else:
                        # Temporary: If no session, Create one? strictly host should start.
                        pass
                elif msg.get("command") == "START_GAME" and player.is_host:
                     session = GameSession(lobby)
                     lobby.game_session = session # Attach to lobby
                     asyncio.create_task(session.start_game())

    except WebSocketDisconnect:
        if lobby and player:
            lobby.disconnect(player)
