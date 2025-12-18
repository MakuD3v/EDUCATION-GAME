import random
import string
from typing import Dict, List, Optional
from fastapi import WebSocket

class Player:
    def __init__(self, websocket: WebSocket, username: str, user_id: int):
        self.websocket = websocket
        self.username = username
        self.user_id = user_id
        self._is_alive = True
        self._is_host = False
        self._score = 0
        self._current_input = None  # To store latest received input

    @property
    def is_alive(self) -> bool:
        return self._is_alive

    @property
    def is_host(self) -> bool:
        return self._is_host
    
    @property
    def score(self) -> int:
        return self._score

    def set_host(self, status: bool):
        self._is_host = status
        
    def eliminate(self):
        self._is_alive = False
        
    def set_score(self, points: int):
        self._score = points
        
    def add_score(self, points: int):
        self._score += points

class Lobby:
    def __init__(self, room_code: str):
        self.room_code = room_code
        self.players: List[Player] = []
        self._is_game_active = False
        self._min_players = 2 # Changed to 2 for dev testing, user said 5
        
    @property
    def host(self) -> Optional[Player]:
        for p in self.players:
            if p.is_host:
                return p
        return None
        
    async def connect(self, player: Player):
        if not self.players:
            player.set_host(True) # First player is host
        self.players.append(player)
        await self.broadcast_player_list()
        
    def disconnect(self, player: Player):
        if player in self.players:
            self.players.remove(player)
            if player.is_host:
                self._migrate_host()
                
    def _migrate_host(self):
        """Transfer host to the next available player."""
        if self.players:
            new_host = self.players[0]
            new_host.set_host(True)
            # Notify everyone (we'd call broadcast here)
            
    async def broadcast(self, message: dict):
        for p in self.players:
            try:
                await p.websocket.send_json(message)
            except:
                pass # Handle stale connections later

    async def broadcast_player_list(self):
        p_list = [{"username": p.username, "is_host": p.is_host, "id": p.user_id} for p in self.players]
        await self.broadcast({"type": "PLAYER_LIST", "players": p_list})

class LobbyManager:
    def __init__(self):
        self.active_lobbies: Dict[str, Lobby] = {}

    def create_lobby(self) -> str:
        """Generate 4-digit numeric code."""
        while True:
            code = "".join(random.choices(string.digits, k=4))
            if code not in self.active_lobbies:
                self.active_lobbies[code] = Lobby(code)
                return code

    def get_lobby(self, code: str) -> Optional[Lobby]:
        return self.active_lobbies.get(code)

    def cleanup(self):
        """Remove empty lobbies."""
        empty_codes = [code for code, lobby in self.active_lobbies.items() if not lobby.players]
        for code in empty_codes:
            del self.active_lobbies[code]

lobby_manager = LobbyManager()
