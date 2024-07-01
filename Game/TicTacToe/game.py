from .strings import *

def printA(arr):
    for i in arr:
        for j in i:
            if(j):
                print(1, end = " ")
            else:
                print(0, end = " ")
        print()
    print("\n")


# В качестве поля в алгоритме используется массив строк m * n, где n - число символов в строке , m - число строк,
#  Содержащая символы: 
# win_score - это количество клеток в ряд, которые должен захватить игрок чтобы победить


# Функция проверяет , является ли данная конфигурация поля выигрышной для кого-то из игроков
# Возвращает символы ❌, ⭕, "ничья" или None (выиграл ❌/ выиграл  ⭕/ ничья или поле не является выигрышным ни для кого из игроков) 
def is_win(FIELD:list[str], win_score:int):

    def d1(y, x):
        return [y - 1, x - 1], [y + 1, x + 1]
    
    def d2(y, x):
        return [y - 1, x + 1], [y + 1, x - 1]
    
    def v(y, x):
        return [y - 1, x], [y + 1, x]
    
    def g(y, x):
        return [y, x + 1], [y, x - 1]
    
    def cell_enumirator(y:int, x:int, symbol:str, direction, checked:list[bool] = None):
        
        if checked is None:
            checked = [[False for _ in range(len(FIELD[0]))] for _ in range(len(FIELD))]
            
        if((x < 0) or (y < 0) or (x >= len(FIELD[0])) or (y >= len(FIELD))): return 0
        if(checked[y][x] or (FIELD[y][x] != symbol)): return 0

        checked[y][x] = True
        cel1, cel2 = direction(y, x)
        result = 1
        result += cell_enumirator(cel1[0], cel1[1], symbol, direction, checked)
        result += cell_enumirator(cel2[0], cel2[1], symbol, direction, checked)
        return  result

    #Проверка , остались ли пустые ячейки на поле
    no_empty = True

    
    for y in range(len(FIELD)):
        for x in range(len(FIELD[0])):
            cell = FIELD[y][x]
            if((cell == SYMBOL_X) or (cell == SYMBOL_O)):
                if(any([
                    cell_enumirator(y, x, cell, d1) >= win_score,
                    cell_enumirator(y, x, cell, d2) >= win_score,
                    cell_enumirator(y, x, cell, v) >= win_score,
                    cell_enumirator(y, x, cell, g) >= win_score,
                    ])): return cell
            if(cell == SYMBOL_UNDEF): no_empty = False

    
    if(no_empty): return "ничья"

    return None


#     def d1(y, x):
#         return [y - 1, x - 1], [y + 1, x + 1]
    
#     def d2(y, x):
#         return [y - 1, x + 1], [y + 1, x - 1]
    
#     def v(y, x):
#         return [y - 1, x], [y + 1, x]
    
#     def g(y, x):
#         return [y, x + 1], [y, x - 1]
    
#     def cell_enumirator(y: int, x: int, symbol: str, direction, checked: list[list[bool]] = None):
#         if checked is None:
#             checked = [[False for _ in range(len(FIELD[0]))] for _ in range(len(FIELD))]
        
#         if (x < 0) or (y < 0) or (x >= len(FIELD[0])) or (y >= len(FIELD)) or checked[y][x] or FIELD[y][x] != symbol:
#             return 0
        
#         checked[y][x] = True
#         cel1, cel2 = direction(y, x)
#         result = 1
#         result += cell_enumirator(cel1[0], cel1[1], symbol, direction, checked)
#         result += cell_enumirator(cel2[0], cel2[1], symbol, direction, checked)
#         return result

#     no_empty = True

#     for y in range(len(FIELD)):
#         for x in range(len(FIELD[0])):
#             cell = FIELD[y][x]
#             if cell in (SYMBOL_X, SYMBOL_O):
#                 if any([
#                     cell_enumirator(y, x, cell, d1) >= win_score,
#                     cell_enumirator(y, x, cell, d2) >= win_score,
#                     cell_enumirator(y, x, cell, v) >= win_score,
#                     cell_enumirator(y, x, cell, g) >= win_score,
#                 ]):
#                     return cell
#             if cell == SYMBOL_UNDEF:
#                 no_empty = False

#     if no_empty:
#         return "ничья"

#     return None

#Функция возвращает True если при данной конфигурации поля очередность хода принадлежит игроку который играет за symbol (❌ или ⭕)
def can_walk(symbol:str, field:str)->bool:
    O_count = 0
    X_count = 0 
    for cell in field:
        if(cell == SYMBOL_O): O_count += 1
        if(cell == SYMBOL_X): X_count += 1

    if(symbol == SYMBOL_O):
        return X_count > O_count
    elif(symbol == SYMBOL_X):
        return X_count == O_count
    else: raise ValueError(f"Unexpected symbol: {symbol}")


def make_game_parametrs(n:int, m:int, win_score:int, bet:int)->str:
    result = "TTT" + str(n) + ":" + str(m) + ":" + str(win_score) + ":" + str(bet)
    return result

def get_game_parametrs(params:str):
    n, m, win_score, bet = map(int, params.split(":")[1:])
    return n, m, win_score, bet








    