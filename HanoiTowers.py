def move_disk(from_peg, to_peg, disk_number):
    """Функция для перемещения диска."""
    move = f"Блин {disk_number}: Стержень {from_peg} -> Стержень {to_peg}."
    print(move)
    return move

def hanoi(n, from_peg, to_peg, aux_peg, moves):
    """Рекурсивная функция для решения задачи Ханойских башен."""
    if n == 1:
        moves.append(move_disk(from_peg, to_peg, n))
    else:
        hanoi(n - 1, from_peg, aux_peg, to_peg, moves)
        moves.append(move_disk(from_peg, to_peg, n))
        hanoi(n - 1, aux_peg, to_peg, from_peg, moves)

def main():
    """Основная функция программы."""
    try:
        num_disks = int(input("Введите количество дисков (положительное число): "))
        if num_disks <= 0:
            raise ValueError("Количество дисков должно быть положительным.")
        
        moves = []
        hanoi(num_disks, 1, 3, 2, moves)  # 1 - начальный стержень, 3 - целевой, 2 - вспомогательный
        
        # Запись решения в файл
        with open("решение.txt", "w", encoding="utf-8") as file:
            for move in moves:
                file.write(move + "n")

    except ValueError as e:
        print(f"Ошибка ввода: {e}")

if __name__ == "__main__":
    main()