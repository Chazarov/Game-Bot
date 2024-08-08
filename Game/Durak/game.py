from enum import Enum
import random
import math
import json

from .strings import *

# Карта определена в виде массива состоящего из двух элементов - list[int, str] 
# сила карты (от 6 до 14) и масть в виде коынстанты, которые определены в Durak.strings
# Список используется вместо отдельного класса для удобного размещения данных в машине состояний
# где могут быть сохранены только базовые типы 


DECK = [[power, suit]
    for suit in [HEARTS_SUIT, DIAMONDS_SUIT, CLUBS_SUIT, SPADES_SUIT]
    for power in range(6, 15)]


class Durak():

    player_decks = list[list[list[int, str]]]# Массив из двух элементов - массивов карт, которые являются колодами игроков
    turn:int
    attacking_player:int
    trump_card:list[int, str]
    deck:list[list[int, str]]
    field:list[list[int, str]]
    card_pool:list[list[int, str]]
    
    #Сделать ПРОВЕРКУ того, может ли игрок сделать такой ход
    #Сделать создание колоды
    # Ход и конфигурация attaked / defended меняется при поддтвердении атакующего игрока 
    def __init__(self):
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        self.player_decks = [list(), list()]
        self.turn = 0 # Определяет чей сейчас ход - первого или второго игрока (по умолчанию первого)

        d = DECK
        random.shuffle(d)

        self.deck = d # колода
        self.trump_card = None  # Карта, которая является козырем
        self.attacking_player = 0 # Игрок, который в данный момент является атакующим (по умолчанию первый)
        self.field = list()  # Игровое поле
        self.card_pool = list() # Карты , которые уже покрыты, но все еще остаются на поле
        
        self.give_cards()



    # Подкинуть карту.
    def to_throw_in(self, player_card_for_turn:int):

        card_for_turn = self.player_decks[self.attacking_player][player_card_for_turn]

        # хватит ли противнику карт, чтобы покрыться
        if(self.attacking_player == 1): defending_player = 0
        else: defending_player = 1
        if(len(self.player_decks[defending_player]) < len(self.field) + 1):
            raise ERRORS[4]

           
        # Есть ли в card_pool карта, имеющая равную актакующей карте силу
        if(len(self.card_pool) != 0):
            if(not any(card[0] == card_for_turn[0] for card in self.card_pool)):
                raise ERRORS[2]

        # Если на поле карт несколько, то имеют ли они силу, равную атакующей карте, 
        # тоесть имеют ли карты, подкинутые одновременно равную силу 
        if(len(self.field) != 0):
            if(not any(card[0] == card_for_turn[0] for card in self.field)):
                raise ERRORS[3]
        

        # Добавление карты на поле
        self.field.append(card_for_turn)

        # Удаление карты из колоды игрока
        self.player_decks[self.attacking_player].pop(player_card_for_turn)

        return None
    


    # Покрыть карту.  Сделать функцию поступательной(обрабатывать по одной покрытой карте)!!!!!!!!!
    def to_cover(self, player_attacking_cart:int, field_attacked_card:int):

        attacking_cart = self.player_decks[self.attacking_player][player_attacking_cart]
        attacked_card = self.field[field_attacked_card]

        if(not (((attacking_cart[0] > attacked_card[0]) and attacking_cart[1] == attacked_card[1]) or \
        attacking_cart[1] == self.trump_card[1])):
            raise(f"It is not possible to cover card {attacked_card} with card {attacked_card}")
        
        self.field.pop(field_attacked_card)
        self.card_pool.append(attacked_card)
        self.card_pool.append(attacking_cart)
        self.player_decks[self.attacking_player].pop(player_attacking_cart)

    def take_cards(self):
        defending_player = None
        if(self.attacking_player == 1): defending_player = 0
        else: defending_player = 1

        for card in self.field:
            self.player_decks[defending_player].append(card)
        self.field = []

    def set_turn(self):
        if(self.turn == 0):
            self.turn = 1
        else:
            self.turn = 0

    def set_attacking_player(self):
        if(self.attacking_player == 0):
            self.attacking_player = 1
        else:
            self.attacking_player = 0

    # Подтвердить ход, проверить победу в игре, сменить ход
    def confirm(self):
        # если ходит атакующий игрок, 
        #   если на поле нет карт - сменяется атакующий игрок
        #   иначе ход переходит к защищаемуся игроку
        # если ходит защищающийся игрок
        #   если на поле нет карт то переход хода к атакующему игроку
        #   иначе игрок сходить не может и берет
        #   !!!!!!!! Сделать константы для состояний для клавиатуры личной колоды игрока !!!!!!!!!
        #                Атака \ Взять \ Подтвердить ход
        if(len(self.deck) == 0 and len(self.player_decks[self.turn]) == 0):
            return WIN

        if(self.turn == self.attacking_player):
            if(len(self.field) == 0):
                self.card_pool = []
                self.give_cards()
                self.set_attacking_player()
                self.set_turn()
            else:
                self.set_turn()
                
        else:
            if(len(self.field) == 0):
                self.set_turn()
            else:
                self.take_cards()
                self.give_cards()
                self.set_turn()



        

        

        


    # Дать из колоды карты игрокам
    def give_cards(self):
        while(   (len(self.player_decks[self.turn]) < 6) and (len(self.deck) != 0)    ):
            self.player_decks[self.turn].append(self.deck.pop())


        another = 2 if self.turn == 1 else 1
        while(   (len(self.player_decks[another]) < 6) and (len(self.deck) != 0)    ):
            self.player_decks[another].append(self.deck.pop())


        
    def can_cover(self, player_attacking_cart:int, field_attacked_card:int) -> bool:

        attacking_cart = self.player_deck[self.attacking_player][player_attacking_cart]
        attacked_card = self.field[field_attacked_card]

        if(not (((attacking_cart[0] > attacked_card[0]) and attacking_cart[1] == attacked_card[1]) or \
        attacking_cart[1] == self.trump_card[1])):
            return ERRORS[5]
        
        return True
        



    def can_throw_in(self, player_card_for_turn:int) -> bool:

        card_for_turn = self.player_deck[self.attacking_player][player_card_for_turn]

        # хватит ли противнику карт, чтобы покрыться
        if(self.attacking_player == 1): defending_player = 0
        else: defending_player = 1
        if(len(self.player_deck[defending_player]) < len(self.field) + 1):
            raise ERRORS[4]

           
        # Есть ли в card_pool карта, имеющая равную актакующей карте силу
        if(len(self.card_pool) != 0):
            if(not any(card[0] == card_for_turn[0] for card in self.card_pool)):
                raise ERRORS[2]

        # Если на поле карт несколько, то имеют ли они силу, равную атакующей карте, 
        # тоесть имеют ли карты, подкинутые одновременно равную силу 
        if(len(self.field) != 0):
            if(not any(card[0] == card_for_turn[0] for card in self.field)):
                raise ERRORS[3]
            
            

    def pack_str(self):

        
        data_dict = {
            "turn":self.turn,
            "trump_card": self.trump_card,
            "attacking_player":self.attacking_player,
            "player_decks":self.player_decks,
            "deck":self.deck,
            "field":self.field,
            "card_pool":self.card_pool,
        }

        data_in_jsonstr = json.dumps(data_dict)

        return data_in_jsonstr


    def unpack_str(self, data:str):
        
        data_dict = json.loads(data)

        self.turn = data_dict["turn"]
        self.trump_card = data_dict["trump_caard"]
        self.attacking_player = data_dict["attacking_player"]
        self.player_decks = data_dict["player_decks"]
        self.deck = data_dict["deck"]
        self.field = data_dict["field"]
        self.card_pool = data_dict["card_pool"]

    def pack_dict(self, data_dict:dict = {}):
        data_dict["turn"] = self.turn
        data_dict["trump_card"] = self.trump_card
        data_dict["attacking_player"] = self.attacking_player
        data_dict["player_decks"] = self.player_decks
        data_dict["deck"] = self.deck
        data_dict["field"] = self.field
        data_dict["card_pool"] = self.card_pool
        return data_dict

    def unpack_dict(self, data:dict):
        self.turn = data["turn"]
        self.trump_card = data["trump_caard"]
        self.attacking_player = data["attacking_player"]
        self.player_decks = data["player_decks"]
        self.deck = data["deck"]
        self.field = data["field"]
        self.card_pool = data["card_pool"]
        




    


def make_start_game_parametrs()->str:
    result = GAME_NAME
    return result

def get_start_game_parametrs(params:str):
    game_name = map(int, params.split("/")[1:])
    return game_name

        