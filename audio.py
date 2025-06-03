import pygame
import os
import sys

def ruta_recurso(rel_path):
    """Devuelve la ruta absoluta del recurso, compatible con PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.abspath("."), rel_path)

class SoundManager:
    def __init__(self):
        # Inicializa el sistema de audio de pygame
        pygame.mixer.init()

        # Carga de sonidos con rutas absolutas
        self.success_sound = pygame.mixer.Sound(ruta_recurso("assets/sounds/success.wav"))
        self.fail_sound = pygame.mixer.Sound(ruta_recurso("assets/sounds/fail.wav"))
        self.victory_sound = pygame.mixer.Sound(ruta_recurso("assets/sounds/victory.wav"))
        self.success_sound.set_volume(1.0)

    def play_success(self):
        self.success_sound.play()

    def play_fail(self):
        self.fail_sound.play()

    def play_victory(self):
        self.victory_sound.play()
