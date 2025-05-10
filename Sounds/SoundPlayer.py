import pygame
import threading
import os
import os


class SoundPlayer:
    def __init__(self):
        os.environ["SDL_AUDIODRIVER"] = "alsa"
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"[SoundPlayer] Audio init failed: {e}")
        self.lock = threading.Lock()

    def play(self, sound_name):
        file_path = os.path.join("Sounds/"+ sound_name + ".mp3")
        print(f"[SoundPlayer] Playing sound: {sound_name}")
        with self.lock:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

    def is_playing(self):
        return pygame.mixer.music.get_busy()
    
    def stop(self):
        with self.lock:
            pygame.mixer.music.stop()
            print("[SoundPlayer] Stopped sound")
