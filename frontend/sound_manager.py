import pygame
import os

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_playing = False
        # Initialize mixer
        try:
            pygame.mixer.init()
        except:
            print("Audio not available")

    def load_sound(self, name, path):
        if not pygame.mixer.get_init(): return
        try:
            if os.path.exists(path):
                self.sounds[name] = pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Failed to load sound {name}: {e}")

    def play_sound(self, name):
        if not pygame.mixer.get_init(): return
        if name in self.sounds:
            self.sounds[name].play()

    def play_music(self, path):
        if not pygame.mixer.get_init(): return
        try:
            if os.path.exists(path):
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(-1) # Loop
                self.music_playing = True
        except Exception as e:
            print(f"Failed to play music: {e}")
