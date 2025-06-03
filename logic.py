import asyncio
import random

class Card:
  def __init__(self,identifier,asset):
    self.id = identifier
    self.asset = asset
    self.revealed = False
    self.matched = False

  def reveal(self):
    """Muestra la carta"""
    if not self.matched:
      self.revealed = True
  
  def hide(self):
    """Oculta la carta"""
    if not self.matched:
      self.revealed = False
  
  def match(self):
    """Confirma que se encontro una pareja de cartas"""
    self.matched = True
  
class memory_card:

  def __init__(self,card_assets:list):

    self.cards = []
    self.first_card = None
    self.second_card = None
    self.locked = False
    self.generate_cards(card_assets) 
  
  def generate_cards(self, assets):
        paired_assets = assets * 2  # Se duplican para formar pares
        random.shuffle(paired_assets)  # Se mezclan aleatoriamente

        self.cards = [Card(i, asset) for i, asset in enumerate(paired_assets)]

  async def click_card(self, card_index):
        if self.locked:
            return  # Si está bloqueado (esperando resultado anterior), ignora

        card = self.cards[card_index]

        # Ignora si ya está visible o emparejada
        if card.revealed or card.matched:
            return

        card.reveal()  # Voltea la carta

        if not self.first_card:
            # Es la primera carta del par
            self.first_card = card
        elif not self.second_card:
            # Es la segunda carta del par
            self.second_card = card
            await self.check_match()  # Verifica si hay coincidencia

  async def check_match(self):
        if self.first_card.asset == self.second_card.asset:
            # Coinciden: marcar ambas como emparejadas
            self.first_card.match()
            self.second_card.match()
            self.reset_selection()
            return  True
            # Aquí deberías emitir sonido y TTS desde la interfaz
        else:
            # No coinciden: se ocultan después de una breve pausa
            self.locked = True  # Bloquea clics adicionales
            await asyncio.sleep(1)
            self.first_card.hide()
            self.second_card.hide()
            self.reset_selection()
            self.locked = False
            return False

  def reset_selection(self):
        self.first_card = None
        self.second_card = None

  def is_finished(self):
        return all(card.matched for card in self.cards)