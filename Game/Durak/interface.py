from .game import Player
from .strings import KARDS_SET


def draw_cards(player:Player):
    result = ""

    for card in player.cards:
        result += KARDS_SET[card.suit][card.power] + "\n"

    return result
