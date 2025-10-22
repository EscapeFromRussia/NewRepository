import sys
import heapq
from Solver import Solver
# --- Константы ---

# Стоимость перемещения для каждого типа
COST = {
    'A': 1,
    'B': 10,
    'C': 100,
    'D': 1000
}

# Целевая комната (индекс) для каждого типа
TARGET_ROOM_IDX = {
    'A': 0,
    'B': 1,
    'C': 2,
    'D': 3
}

# Ожидаемый обитатель для каждой комнаты
ROOM_TARGET_TYPE = ['A', 'B', 'C', 'D']

# Позиция "портала" в коридоре для каждой комнаты
PORTAL_POS = [2, 4, 6, 8]

# Разрешенные позиции для остановки в коридоре (индексы)
STOP_POS = {0, 1, 3, 5, 7, 9, 10}

# Глубина комнат
ROOM_DEPTH = 2


def main():
    # Чтение входных данных
    lines = []
    for line in sys.stdin:
        lines.append(line.rstrip('\n'))

    result = Solver().solve(lines)
    print(result)


if __name__ == "__main__":
    main()
