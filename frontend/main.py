import asyncio
import pygame
from .network import NetworkManager
from .ui_elements import Button, Label, Popup, MobileKeyButton
from .input_box import InputBox
from .sound_manager import SoundManager

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# States
MENU = "MENU"
LOBBY = "LOBBY"
GAME = "GAME"

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("EDU PARTY")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = MENU
        self.network = NetworkManager()
        self.client_id = 123 # Random ID for now
        self.sound_manager = SoundManager()
        
        # Data
        self.lobby_code = ""
        self.player_list = []
        self.popup = None # Active popup overlay
        self.current_round = 0
        self.round_instruction = ""
        self.game_timer = 0

        # UI Components
        self._init_ui()

    def _init_ui(self):
        # Menu UI
        self.btn_create = Button(300, 200, 200, 50, "Create Lobby", self.create_lobby)
        self.btn_join = Button(300, 300, 200, 50, "Join Lobby", self.join_lobby_prompt)
        
        # Lobby UI
        self.lbl_lobby = Label(50, 50, "Lobby: ???")
        self.lbl_players = Label(50, 100, "Players: 0")
        self.btn_start = Button(300, 500, 200, 50, "START GAME", self.start_game, color=(200, 100, 100))
        self.is_host = False
        
        # Game UI
        self.lbl_round = Label(350, 20, "Round 1")
        self.lbl_instruction = Label(50, 100, "Waiting...", font_size=48)
        self.input_box = InputBox(300, 250, 140, 32)
        self.lbl_status = Label(300, 300, "", font_size=24, color=(200, 50, 50))
        self.btn_kbd = MobileKeyButton(self.toggle_keyboard)
        
        # Practice Mode Button (Menu)
        self.btn_practice = Button(300, 400, 200, 50, "Practice Mode", self.start_practice)

    def toggle_keyboard(self):
        # Trigger Pygame/SDL keyboard event
        if pygame.key.get_repeat()[0] == 0:
            pygame.key.set_repeat(500, 50) # Enable repeat
        pygame.key.start_text_input() # For SDL2 / Emscripten

    def start_practice(self):
        # TODO: Implement local practice logic
        self.state = GAME
        self.lbl_instruction.set_text("PRACTICE: 5 + 5 = ?")
        self.current_round = 0

    def dismiss_popup(self):
        self.popup = None

    def create_lobby(self):
        asyncio.create_task(self._async_create_lobby())

    async def _async_create_lobby(self):
        await self.network.connect_websocket(self.client_id)
        await self.network.send({"command": "CREATE", "username": "HostPlayer"})
        self.is_host = True

    def start_game(self):
         asyncio.create_task(self._async_start_game())

    async def _async_start_game(self):
        await self.network.send({"command": "START_GAME"})

    def join_lobby_prompt(self):
        # In real app, popup input box. Hardcoding for MVP.
        pass

    async def update(self):
        self.screen.fill((30, 30, 30))
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.popup:
                self.popup.handle_event(event)
                continue # Block other input

            if self.state == MENU:
                self.btn_create.handle_event(event)
                self.btn_join.handle_event(event)
                self.btn_practice.handle_event(event)
            elif self.state == LOBBY:
                if self.is_host:
                    self.btn_start.handle_event(event)
            elif self.state == GAME:
                self.btn_kbd.handle_event(event)
                submit_text = self.input_box.handle_event(event)
                if submit_text:
                    if self.current_round == 0: # Practice
                        if submit_text == "10":
                             self.lbl_status.set_text("Correct! (Practice)")
                        else:
                             self.lbl_status.set_text("Wrong! (Practice)")
                    else:
                        asyncio.create_task(self.submit_answer(submit_text))
                    
                    self.input_box.text = "" # Clear after send
                    self.input_box.txt_surface = self.input_box.font.render("", True, self.input_box.color)

        # Draw
        if self.state == MENU:
            self.btn_create.draw(self.screen)
            self.btn_join.draw(self.screen)
            self.btn_practice.draw(self.screen)
        elif self.state == LOBBY:
            self.lbl_lobby.draw(self.screen)
            self.lbl_players.draw(self.screen)
            if self.is_host:
                self.btn_start.draw(self.screen)
        elif self.state == GAME:
            self.lbl_round.draw(self.screen)
            self.lbl_instruction.draw(self.screen)
            self.input_box.draw(self.screen)
            self.lbl_status.draw(self.screen)
            self.btn_kbd.draw(self.screen)
            
        if self.popup:
            self.popup.draw(self.screen)

        # Network Messages
        if self.network.ws:
            try:
                msg = await asyncio.wait_for(self.network.receive(), timeout=0.01)
                if msg:
                    self.handle_message(msg)
            except asyncio.TimeoutError:
                pass

        pygame.display.flip()
        await asyncio.sleep(0)

    async def submit_answer(self, text):
        # Send answer to backend
        await self.network.send({"command": "GAME_INPUT", "input": text})

    def handle_message(self, msg):
        if msg["type"] == "LOBBY_CREATED":
            self.lobby_code = msg["code"]
            self.state = LOBBY
            self.lbl_lobby.set_text(f"Lobby: {self.lobby_code}")
        elif msg["type"] == "LOBBY_JOINED":
            self.lobby_code = msg["code"]
            self.state = LOBBY
            self.lbl_lobby.set_text(f"Lobby: {self.lobby_code}")
        elif msg["type"] == "PLAYER_LIST":
            self.player_list = msg["players"]
            self.lbl_players.set_text(f"Players: {len(self.player_list)}")
        elif msg["type"] == "GAME_START":
            self.state = GAME
        elif msg["type"] == "ROUND_START":
            self.current_round = msg["round"]
            self.lbl_round.set_text(f"Round {self.current_round}")
            self.lbl_instruction.set_text(msg["instruction"])
            self.lbl_status.set_text("") 
            # Show popup
            self.popup = Popup(200, 150, 400, 300, f"ROUND {self.current_round}\n\n{msg['instruction']}", self.dismiss_popup)
        elif msg["type"] == "ROUND_END":
             self.lbl_status.set_text("Round Ended!")
        elif msg["type"] == "ELIMINATED":
             self.lbl_status.set_text("ELIMINATED!")
             # Show logic?

async def main():
    game = Game()
    while game.running:
        await game.update()
        game.clock.tick(FPS)
    await game.network.close()

if __name__ == "__main__":
    asyncio.run(main())
