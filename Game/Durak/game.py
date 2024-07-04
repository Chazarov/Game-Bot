from enum import Enum
import random
import math
from .strings import *

class Card():
    power:int # Сила карты от 6 до 14
    suit:str # Масть. Строки , определяющие Масти перечислены в Durak/strings.py

class Player():
    cards:list[Card]

class Durak():
    player1:Player
    player2:Player

    cards:set[Card]
    trump_card:Card#Карта которая является козырем

    attacing_player:int#0 или 1 в зависимости от того, какой игрок защищается ("кроется")
    field:list[Card]#Игровое поле

    # Подкинуть карту.
    # idx_cards_for_turn - массив индексов тех карт игрока ,которыми он ходит
    def to_throw_in(self, idx_cards_for_turn :list[int]):

        if(len(idx_cards_for_turn) == 0):
            raise("length of a cards can't be a zero")
        

        if(self.attacing_player == 1):
            player = self.player1
        elif(self.attacing_player == 2):
            player = self.player2


        cards_for_turn = []
        for card_idx in idx_cards_for_turn:
            cards_for_turn.append(player.cards[card_idx])
        
        #Сделать проверку на то , что у противника хватит карт, чтобы покрыться

        # Проверка, чтобы карты выброшенные игроком (если их несколько) имели одинаковую силу
        card_power = cards_for_turn[0].power
        for i in range(1, len(cards_for_turn)):
            if(card_power != cards_for_turn[i].power):
                return ERRORS["1"]
            

        for card in cards_for_turn:
            self.field.append(card)

        return None
    
    # Покрыть карты.  Сделать функцию поступательной(обрабатывать по одной покрытой карте)!!!!!!!!!
    def to_cover(self, ):
        pass
        
            

        


        