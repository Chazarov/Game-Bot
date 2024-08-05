from .game import Player, Card
from .strings import KARDS_SET


def draw_player_cards(player:Player):
    result = ""

    for card in player.cards:
        result += KARDS_SET[card.suit][card.power] + "\n"

    return result

def draw_card(card:Card = None, card_parametrs:list[int, str] = None, mini:bool = True):

    if(card != None):
        return KARDS_SET[card.suit][card.power]
    elif(card_parametrs != None):
        return KARDS_SET[card_parametrs[1]][card_parametrs[0]]
    else:
        return None
    


def draw_choisen_card(card:Card):
    result = draw_card(card = card, mini = True) + "\n ☝️"
    return result

def make_cards_parametrs_list(cards:list[Card]):
    result = list()
    for card in cards:
        result.append([card.power, card.suit])

    return result

def make_cards_list(cards:list[list[int, str]]):
    result = list()
    for card in cards:
        result.append(Card(power = card[0], suit = card[1]))
        
    return result
     

    
