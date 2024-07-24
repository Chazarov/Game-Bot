GAME_NAME = "Tic_Tac_Toe"

# символы, которые используются:
SYMBOL_X = '❌'
SYMBOL_O = '⭕'
SYMBOL_UNDEF = '◻'

def make_start_game_parametrs(n:int, m:int, win_score:int, bet:int)->str:
    result = GAME_NAME + ":" + str(n) + ":" + str(m) + ":" + str(win_score) + ":" + str(bet)
    return result

def get_start_game_parametrs(data:str):
    game_name, n, m, win_score, bet = data.split(":")
    return game_name, n, m, win_score, bet


def make_game_configuration(m:int, n:int, field:str):
    result = GAME_NAME + ":" + str(n) + ":" + str(m) + ":" + field
    return result

def get_game_configuration(data:str):
    game_name, n, m = data.split(":")[1:]
    return game_name, n, m
