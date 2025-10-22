#!/usr/bin/env python3
import sys
import heapq

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


# --- /Константы ---


def solve(lines: list[str]) -> int:
    """
    Решение задачи о сортировке в лабиринте с использованием алгоритма Дейкстры.

    Args:
        lines: список строк, представляющих лабиринт

    Returns:
        минимальная энергия для достижения целевой конфигурации
    """

    # --- 1. Парсинг и инициализация ---

    # Коридор: кортеж из 11 символов ('.', 'A', 'B', 'C', 'D')
    initial_hallway = tuple(lines[1][1:12])

    # Комнаты: кортеж из 4 кортежей (по 2 символа в каждом)
    # (('B', 'A'), ('C', 'D'), ('B', 'C'), ('D', 'A'))
    initial_rooms_list = [
        (lines[2][3], lines[3][3]),
        (lines[2][5], lines[3][5]),
        (lines[2][7], lines[3][7]),
        (lines[2][9], lines[3][9])
    ]
    initial_rooms = tuple(initial_rooms_list)

    initial_state = (initial_hallway, initial_rooms)

    # Целевая конфигурация
    target_state = (
        ('.',) * 11,
        (
            ('A', 'A'),
            ('B', 'B'),
            ('C', 'C'),
            ('D', 'D')
        )
    )

    # Очередь с приоритетом (min-heap) для алгоритма Дейкстры
    # (cost, state)
    pq = [(0, initial_state)]

    # Словарь для хранения минимальной стоимости
    # {state: min_cost}
    min_costs = {initial_state: 0}

    # --- 2. Алгоритм Дейкстры ---

    while pq:
        cost, current_state = heapq.heappop(pq)
        hallway, rooms = current_state

        # Цель достигнута
        if current_state == target_state:
            return cost

        # Если мы нашли более дешевый путь к этому состоянию ранее, пропускаем
        if cost > min_costs.get(current_state, float('inf')):
            continue

        # --- 3. Генерация ходов ---

        # === Движение 1: Из комнаты в коридор ===
        for room_idx in range(4):
            room = rooms[room_idx]
            target_type = ROOM_TARGET_TYPE[room_idx]

            # Проверяем, нужно ли двигать кого-то из этой комнаты.
            # Если комната пуста или уже содержит *только* правильные типы,
            # то двигать из нее никого не нужно.
            if all(amphipod == '.' or amphipod == target_type for amphipod in room):
                continue

            # Находим самого верхнего объекта, которого можно подвинуть
            for depth_idx, amphipod_to_move in enumerate(room):
                if amphipod_to_move != '.':
                    # Нашли объект, который будем двигать
                    steps_to_exit = depth_idx + 1
                    portal = PORTAL_POS[room_idx]

                    # Проверяем все возможные места остановки в коридоре
                    for stop_pos in STOP_POS:
                        # Проверяем, свободен ли путь от портала до места остановки
                        path_start = min(portal, stop_pos)
                        path_end = max(portal, stop_pos)

                        # Определяем срезы для проверки пути
                        if stop_pos < portal:
                            path_indices = range(stop_pos, portal)
                        else:
                            path_indices = range(portal + 1, stop_pos + 1)

                        if all(hallway[i] == '.' for i in path_indices):
                            # Путь свободен, генерируем новое состояние
                            move_cost = (steps_to_exit + abs(stop_pos - portal)) * COST[amphipod_to_move]
                            new_total_cost = cost + move_cost

                            # Создаем новое состояние (неизменяемое)
                            new_hallway = list(hallway)
                            new_hallway[stop_pos] = amphipod_to_move

                            new_rooms = list(list(r) for r in rooms)
                            new_rooms[room_idx][depth_idx] = '.'

                            new_state = (tuple(new_hallway), tuple(tuple(r) for r in new_rooms))

                            if new_total_cost < min_costs.get(new_state, float('inf')):
                                min_costs[new_state] = new_total_cost
                                heapq.heappush(pq, (new_total_cost, new_state))

                    # Мы двигаем только самого верхнего, поэтому выходим из цикла глубины
                    break

                    # === Движение 2: Из коридора в комнату ===
        for hall_idx, amphipod in enumerate(hallway):
            if amphipod == '.':
                continue

            target_room_idx = TARGET_ROOM_IDX[amphipod]
            target_room = rooms[target_room_idx]
            portal = PORTAL_POS[target_room_idx]

            # Правило 2: Проверяем, "чиста" ли комната
            if not all(a == '.' or a == amphipod for a in target_room):
                continue

            # Проверяем, свободен ли путь в коридоре до портала
            if hall_idx < portal:
                path_indices = range(hall_idx + 1, portal + 1)
            else:
                path_indices = range(portal, hall_idx)

            if not all(hallway[i] == '.' for i in path_indices):
                continue  # Путь заблокирован

            # Путь свободен, комната "чиста". Можно заходить.
            # Правило 4: Находим самую глубокую доступную позицию
            dest_depth = -1
            if target_room[1] == '.':
                dest_depth = 1
            elif target_room[0] == '.':
                dest_depth = 0

            # Если dest_depth == -1, комната полна (это не должно случиться,
            # если целевая конфигурация еще не достигнута, но проверка не помешает)
            if dest_depth == -1:
                continue

            # Считаем стоимость
            hall_steps = abs(hall_idx - portal)
            room_steps = dest_depth + 1
            move_cost = (hall_steps + room_steps) * COST[amphipod]
            new_total_cost = cost + move_cost

            # Генерируем новое состояние
            new_hallway = list(hallway)
            new_hallway[hall_idx] = '.'

            new_rooms = list(list(r) for r in rooms)
            new_rooms[target_room_idx][dest_depth] = amphipod

            new_state = (tuple(new_hallway), tuple(tuple(r) for r in new_rooms))

            # Добавляем в очередь, если нашли более дешевый путь
            if new_total_cost < min_costs.get(new_state, float('inf')):
                min_costs[new_state] = new_total_cost
                heapq.heappush(pq, (new_total_cost, new_state))

    # Если цикл завершился, а цель не найдена
    return -1


def main():
    # Чтение входных данных
    lines = []
    for line in sys.stdin:
        lines.append(line.rstrip('\n'))

    result = solve(lines)
    print(result)


if __name__ == "__main__":
    main()
