import pygame

class SoundManager:
    def __init__(self):
        # Inicializa el sistema de audio de pygame
        pygame.mixer.init()

        # Carga de sonidos
        self.success_sound = pygame.mixer.Sound("assets/sounds/success.wav")
        self.fail_sound = pygame.mixer.Sound("assets/sounds/fail.wav")
        self.victory_sound = pygame.mixer.Sound("assets/sounds/victory.wav")
        self.success_sound.set_volume(1.0)

    def play_success(self):
        self.success_sound.play()
        

    def play_fail(self):
        self.fail_sound.play()

    def play_victory(self):
        self.victory_sound.play()