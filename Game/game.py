from .strings import *

# В качестве поля в алгоритме используется массив строк m * n, где n - число символов в строке , m - число строк,
#  Содержащая символы: 
# win_score - это количество клеток в ряд, которые должен захватить игрок чтобы победить


# Функция проверяет , является ли данная конфигурация поля выигрышной для кого-то из игроков
# Возвращает символы ❌, ⭕, "ничья" или None (выиграл ❌/ выиграл  ⭕/ ничья или поле не является выигрышным ни для кого из игроков) 
def is_win(FIELD:list[str], win_score:int):

    def d1(y, x):
        return [y - 1, x - 1], [x + 1, y + 1]
    
    def d2(y, x):
        return [y - 1, x + 1], [y + 1, x - 1]
    
    def v(yy, xx):
        return [yy - 1, xx], [yy + 1, xx]
    
    def g(y, x):
        return [y, x + 1], [y, x - 1]
    
    def cell_enumirator(y:int, x:int, symbol:str, direction, checked:list = None):
        if(checked == None): checked = [[False for i in range(len(FIELD))] for i in range(len(FIELD[0]))]
        if((x < 0) or (y < 0) or (x >= len(FIELD[0])) or (y >= len(FIELD))): return 0
        if((checked[y][x] == True) or (FIELD[y][x] != symbol)): return 0

        checked[y][x] = True
        cel1, cel2 = direction(y, x)
        result = 1
        result += cell_enumirator(cel1[0], cel1[1], symbol, direction, checked)
        result += cell_enumirator(cel2[0], cel2[1], symbol, direction, checked)
        return  result

    no_empty = True

    for y in range(len(FIELD)):
        for x in range(len(FIELD[0])):
            cell = FIELD[y][x]
            if((cell == SYMBOL_X) or (cell == SYMBOL_O)):
                if(any([
                    cell_enumirator(y, x, cell, d1) == win_score,
                    cell_enumirator(y, x, cell, d2) == win_score,
                    cell_enumirator(x, y, cell, v) == win_score,
                    cell_enumirator(y, x, cell, g) == win_score,
                    ])): return cell
            if(cell == SYMBOL_UNDEF): no_empty = False

    
    if(no_empty): return "ничья"

    return None


#Функция возвращает True если при данной конфигурации поля очередность хода принадлежит игроку который играет за symbol (❌ или ⭕)
def can_walk(symbol:str, field:str)->bool:
    O_count = 0
    X_count = 0 
    for i in range(len(field)):
        for cell in field[i]: 
            if(cell == SYMBOL_O): O_count += 1
            if(cell == SYMBOL_X): X_count += 1

    if(symbol == SYMBOL_O):
        if(X_count > O_count): return True
        else: return False
    elif(symbol == SYMBOL_X):
        if(O_count == X_count): return True
        else: return False
    else: return None







    