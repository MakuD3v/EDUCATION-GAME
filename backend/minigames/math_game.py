from .base import BaseGame
import random

class MathGame(BaseGame):
    def __init__(self, difficulty: int = 1):
        super().__init__(difficulty)
        self.problem = ""
        self.answer = 0
        self._generate_problem()

    def _generate_problem(self):
        if self._difficulty == 1:
            a, b = random.randint(1, 10), random.randint(1, 10)
            self.problem = f"{a} + {b}"
            self.answer = a + b
        elif self._difficulty == 2:
            a, b = random.randint(10, 50), random.randint(1, 10)
            self.problem = f"{a} - {b}"
            self.answer = a - b
        else:
            a, b = random.randint(5, 12), random.randint(5, 12)
            self.problem = f"{a} * {b}"
            self.answer = a * b

    def get_instructions(self) -> str:
        return f"Solve the math problem: {self.problem}"

    def start_game(self):
        # Logic to start timer?
        pass

    def process_input(self, player_id: str, input_data: any) -> bool:
        try:
            val = int(input_data)
            return val == self.answer
        except:
            return False

    def check_win_condition(self, player_id: str) -> bool:
        # In "First to Score", this might just return True if they got it right
        return False
