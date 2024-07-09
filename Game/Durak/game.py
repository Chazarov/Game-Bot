from enum import Enum
import random
import math
from .strings import *

class Card():
    def __init__(self, power: int, suit: str):
        self.power = power  # Сила карты от 6 до 14
        self.suit = suit  # Масть. Строки, определяющие масти, перечислены в Durak/strings.py

class Player():
    def __init__(self):
        self.cards = []  # Список карт игрока

class Durak():
    #Сделать ПРОВЕРКУ того, может ли игрок сделать такой ход
    #Сделать создание колоды
    # Ход и конфигурация attaked / defended меняется при поддтвердении атакующего игрока 
    def __init__(self):
        self.players = [Player(), Player()]
        self.turn = 1 # Определяет чей сейчас ход - первого или второго игрока (по умолчанию первого)

        self.deck = set()
        self.trump_card = None  # Карта, которая является козырем
        self.attacking_player = 1 # Игрок, который в данный момент является атакующим (по умолчанию первый)
        self.field = []  # Игровое поле
        self.card_pool = [] # Карты , которые уже покрыты, но все еще остаются на поле

    



    # Подкинуть карту.
    def to_throw_in(self, player_card_for_turn:int):

        card_for_turn = self.players[self.attacking_player].cards[player_card_for_turn]

        # хватит ли противнику карт, чтобы покрыться
        if(self.attacking_player == 1): defending_player = 0
        else: defending_player = 1
        if(len(self.players[defending_player].cards) < len(self.field) + 1):
            raise ERRORS[4]

           
        # Есть ли в card_pool карта, имеющая равную актакующей карте силу
        if(len(self.card_pool) != 0):
            if(not any(card.power == card_for_turn.power for card in self.card_pool)):
                raise ERRORS[2]

        # Если на поле карт несколько, то имеют ли они силу, равную атакующей карте, 
        # тоесть имеют ли карты, подкинутые одновременно равную силу 
        if(len(self.field) != 0):
            if(not any(card.power == card_for_turn.power for card in self.field)):
                raise ERRORS[3]
        

        # Добавление карты на поле
        self.field.append(card_for_turn)

        # Удаление карты из колоды игрока
        self.players[self.attacking_player].cards.pop(player_card_for_turn)

        return None
    


    # Покрыть карту.  Сделать функцию поступательной(обрабатывать по одной покрытой карте)!!!!!!!!!
    def to_cover(self, player_attacking_cart:int, field_attacked_card:int):

        attacking_cart = self.players[self.attacking_player].cards[player_attacking_cart]
        attacked_card = self.field[field_attacked_card]

        if(not (((attacking_cart.power > attacked_card.power) and attacking_cart.suit == attacked_card.suit) or \
        attacking_cart.suit == self.trump_card.suit)):
            raise(f"It is not possible to cover card {attacked_card} with card {attacked_card}")
        
        self.field.pop(field_attacked_card)
        self.card_pool.append(attacked_card)
        self.card_pool.append(attacking_cart)
        self.players[self.attacking_player].cards.pop(player_attacking_cart)



    # Подтвердить ход и проверить победу в игре
    def confirm(self):
        self.card_pool = []

        if(len(self.deck) == 0 and len(self.players[self.turn].cards) == 0):
            return WIN

        self.give_cards(self.turn)


    # Дать из колоды карты игроку
    def give_cards(self, player_number:int):
        while(   (len(self.players[player_number].cards) < 6) and (len(self.deck) != 0)    ):
            self.players[player_number].cards.append(self.deck.pop())


        
    def can_cover(self, player_attacking_cart:int, field_attacked_card:int) -> bool:

        attacking_cart = self.players[self.attacking_player].cards[player_attacking_cart]
        attacked_card = self.field[field_attacked_card]

        if(not (((attacking_cart.power > attacked_card.power) and attacking_cart.suit == attacked_card.suit) or \
        attacking_cart.suit == self.trump_card.suit)):
            return ERRORS[5]
        
        return True
        



    def can_throw_in(self, player_card_for_turn:int) -> bool:

        card_for_turn = self.players[self.attacking_player].cards[player_card_for_turn]

        # хватит ли противнику карт, чтобы покрыться
        if(self.attacking_player == 1): defending_player = 0
        else: defending_player = 1
        if(len(self.players[defending_player].cards) < len(self.field) + 1):
            raise ERRORS[4]

           
        # Есть ли в card_pool карта, имеющая равную актакующей карте силу
        if(len(self.card_pool) != 0):
            if(not any(card.power == card_for_turn.power for card in self.card_pool)):
                raise ERRORS[2]

        # Если на поле карт несколько, то имеют ли они силу, равную атакующей карте, 
        # тоесть имеют ли карты, подкинутые одновременно равную силу 
        if(len(self.field) != 0):
            if(not any(card.power == card_for_turn.power for card in self.field)):
                raise ERRORS[3]


        
        
            

        


        