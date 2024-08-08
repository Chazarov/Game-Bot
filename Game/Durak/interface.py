import math

from .strings import KARDS_SET, BIG_KARDS_SET


def draw_cards(cards:list[list[int, str]], cards_in_row:int, card_lines_count:int, separator:str):

    result = ""
    cards_list = []
    for card in cards:
        cards_list.append(KARDS_SET[card[1]][card[0]].split("\n")) 

    print(math.ceil(len(cards_list)/cards_in_row))
    for i in range(math.ceil(len(cards_list)/cards_in_row)):
        cards_selection = cards_list[i*cards_in_row:][:cards_in_row]
        print("<<<<<<<")
        for j in range(card_lines_count):
            for card in cards_selection:
                result += card[j] + separator
            result += "\n"
        result += "\n\n"


    

    

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
     

    
