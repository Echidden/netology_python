print('Количество столбцов долек:')
n = int(input())
print('Количество рядов долек:')
m = int(input())


def min_breaks(n, m):
    if n == 1 and m == 1:
        return 0
    elif n == 1:
        return m - 1
    elif m == 1:
        return n - 1
    else:
        pieces = n*m
        return pieces - 1


print("Количество разломов:", min_breaks(n, m))