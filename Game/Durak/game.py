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



        