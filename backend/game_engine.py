import asyncio
from typing import List, Optional
from .lobby_system import Player, Lobby
from .minigames.base import BaseGame

class GameSession:
    """
    Manages the game flow: Rounds 1-4, Logic Checks, Elimination.
    """
    def __init__(self, lobby: Lobby):
        self._lobby = lobby
        self._current_round = 0
        self._max_rounds = 4
        self._active_minigame: Optional[BaseGame] = None
        self._is_running = False

    @property
    def round_number(self) -> int:
        return self._current_round

    async def start_game(self):
        """Main Game Loop."""
        self._is_running = True
        self._current_round = 0
        
        # Reset scores
        for p in self._lobby.players:
            p.set_score(0)
            
        await self._lobby.broadcast({"type": "GAME_START"})
        
        while self._current_round < self._max_rounds and self._is_running:
            self._current_round += 1
            await self._play_round()
            
            if self._current_round < 4:
                await self._logic_check_elimination()
            else:
                await self._declare_winner()

        self._is_running = False

    async def _play_round(self):
        """Round execution logic."""
        # 1. Select Minigame (Random placeholder for now)
        from .minigames.math_game import MathGame
        self._active_minigame = MathGame(difficulty=self._current_round)
        
        await self._lobby.broadcast({
            "type": "ROUND_START", 
            "round": self._current_round,
            "instruction": self._active_minigame.get_instructions()
        })
        
        # Simulating round time for prototype (30s)
        # Real logic: Wait for timer OR all finished
        for i in range(30):
            if not self._is_running: break
            await asyncio.sleep(1)
        
        await self._lobby.broadcast({"type": "ROUND_END"})

    async def handle_input(self, player: Player, input_data: str):
        if not self._active_minigame:
            return

        is_correct = self._active_minigame.process_input(player.user_id, input_data)
        if is_correct:
            # First to score logic? Or Accumulate?
            # User said: "First to score" in Q2.
            # Let's give points = Speed? Or flat 100?
            player.add_score(100)
            await player.websocket.send_json({"type": "gamestate", "msg": "Correct!"})
        else:
             await player.websocket.send_json({"type": "gamestate", "msg": "Wrong!"})

    async def _logic_check_elimination(self):
        """50% Elimination Rule."""
        # Sort by score descending
        sorted_players = sorted(
            [p for p in self._lobby.players if p.is_alive],
            key=lambda p: p.score,
            reverse=True
        )
        
        count = len(sorted_players)
        if count <= 1:
            return # Don't eliminate if only 1 left

        # Calculate cutoff (Round up to keep more players? or Round down?)
        # User said: 30 -> 15 -> 7 -> 1.
        # 30 / 2 = 15.
        # 15 / 2 = 7.5 -> 7?
        cutoff_index = count // 2
        
        # Keep top half
        survivors = sorted_players[:cutoff_index]
        eliminated = sorted_players[cutoff_index:]
        
        # Update Status
        for p in eliminated:
            p.eliminate()
            await p.websocket.send_json({"type": "ELIMINATED"})
            
        # Reset scores for next round? User said "They reset" in Q7.
        for p in survivors:
            p.set_score(0)
            
        await self._lobby.broadcast({
            "type": "LOGIC_CHECK",
            "alive_count": len(survivors),
            "eliminated_count": len(eliminated)
        })
        
        await asyncio.sleep(3) # Pausing for dramatic effect

    async def _declare_winner(self):
        """Round 4 Sudden Death Result."""
        # Sort by score (Sudden Death)
        sorted_players = sorted(
            [p for p in self._lobby.players if p.is_alive],
            key=lambda p: p.score,
            reverse=True
        )
        
        if sorted_players:
            winner = sorted_players[0]
            # Ensure winner actually has score?
            if winner.score > 0:
                await self._lobby.broadcast({
                    "type": "GAME_OVER",
                    "winner": winner.username,
                    "winner_id": winner.user_id
                })
            else:
                 await self._lobby.broadcast({"type": "GAME_OVER", "winner": "Draw (No Score)"})
            # Save stats to DB logic here
        else:
            await self._lobby.broadcast({"type": "GAME_OVER", "winner": "No One"})
