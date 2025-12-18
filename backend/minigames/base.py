from abc import ABC, abstractmethod

class BaseGame(ABC):
    """
    Abstract Base Class for all Mini-Games.
    Enforces a strict interface for starting, updating, and scoring.
    """
    
    def __init__(self, difficulty: int = 1):
        self._difficulty = difficulty
        self._is_completed = False
        
    @property
    def difficulty(self) -> int:
        return self._difficulty

    @property
    def is_completed(self) -> bool:
        return self._is_completed

    @abstractmethod
    def get_instructions(self) -> str:
        """Return the 'How to Play' text for the popup."""
        pass

    @abstractmethod
    def start_game(self):
        """Initialize the game state logic."""
        pass

    @abstractmethod
    def process_input(self, player_id: str, input_data: any) -> bool:
        """Process player input. Return True if input was valid/correct."""
        pass

    @abstractmethod
    def check_win_condition(self, player_id: str) -> bool:
        """Check if a specific player has met the win criteria."""
        pass

    def finish_game(self):
        """Mark game as done."""
        self._is_completed = True
