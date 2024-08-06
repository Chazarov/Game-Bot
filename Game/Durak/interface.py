from .game import Player
from .strings import KARDS_SET, BIG_KARDS_SET


def draw_player_cards(player:list[list[int, str]]):
    result = ""

    for card in player:
        result += KARDS_SET[card[1]][card[0]] + "\n"

    return result

def draw_card(card:list[int, str] = None, mini:bool = True):

    if(mini):
        return KARDS_SET[card[1]][card[0]]
    else:
        return BIG_KARDS_SET[card[1]][card[0]]
    


def draw_choisen_card(card:list[int, str]):
    result = draw_card(card = card, mini = True) + "\n ☝️"
    return result

def make_cards_parametrs_list(cards:list[list[int, str]]):
    result = list()
    for card in cards:
        result.append([card[0], card[1]])

    return result

def make_cards_list(cards:list[list[int, str]]):
    result = list()
    for card in cards:
        result.append(list[int, str](power = card[0], suit = card[1]))
        
    return result
     

    
