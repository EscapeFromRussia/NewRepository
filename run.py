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

# Глубина комнат (будет определена из входных данных)
# ROOM_DEPTH = 2 (Убрано, т.к. теперь динамическое)

# --- /Константы ---


def solve(lines: list[str]) -> int:
    """
    Решение задачи о сортировке в лабиринте с использованием алгоритма Дейкстры.
    Работает для комнат глубиной 2 и 4.

    Args:
        lines: список строк, представляющих лабиринт

    Returns:
        минимальная энергия для достижения целевой конфигурации
    """
    
    # --- 1. Определение глубины и парсинг ---

    # Определяем глубину по количеству строк (5 строк для глубины 2, 7 для глубины 4)
    if len(lines) == 5:
        room_depth = 2
    elif len(lines) == 7:
        room_depth = 4
    else:
        raise ValueError("Неподдерживаемый формат ввода: ожидалось 5 или 7 строк")

    # Коридор: кортеж из 11 символов ('.', 'A', 'B', 'C', 'D')
    initial_hallway = tuple(lines[1][1:12])
    
    # Динамический парсинг комнат
    # Индексы колонок в строках
    room_cols = [3, 5, 7, 9]
    temp_rooms = [[] for _ in range(4)]
    
    for r_idx in range(room_depth):
        # Строки комнат начинаются со 2-й (индекс 2)
        line = lines[2 + r_idx]
        for c_idx in range(4):
            col_pos = room_cols[c_idx]
            temp_rooms[c_idx].append(line[col_pos])
            
    # Преобразуем в кортеж кортежей
    # (('B', 'A'), ('C', 'D'), ...) или (('B', 'D', 'D', 'A'), ...)
    initial_rooms = tuple(tuple(room) for room in temp_rooms)
    
    initial_state = (initial_hallway, initial_rooms)

    # Динамическое создание целевой конфигурации
    target_rooms = tuple(
        (ROOM_TARGET_TYPE[i],) * room_depth for i in range(4)
    )
    target_state = (
        ('.',) * 11,
        target_rooms
    )

    # --- 2. Алгоритм Дейкстры ---

    # Очередь с приоритетом (min-heap) для алгоритма Дейкстры
    # (cost, state)
    pq = [(0, initial_state)]
    
    # Словарь для хранения минимальной стоимости
    # {state: min_cost}
    min_costs = {initial_state: 0}

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
                continue # Путь заблокирован

            # Путь свободен, комната "чиста". Можно заходить.
            # Правило 4: Находим самую глубокую доступную позицию
            
            dest_depth = -1
            # Ищем снизу вверх (от room_depth - 1 до 0)
            for d in range(room_depth - 1, -1, -1):
                if target_room[d] == '.':
                    dest_depth = d
                    break # Нашли самую глубокую свободную позицию
            
            # Если dest_depth == -1, комната полна
            if dest_depth == -1:
                continue

            # Считаем стоимость
            hall_steps = abs(hall_idx - portal)
            room_steps = dest_depth + 1 # Шаги для входа в комнату (1 для индекса 0, ... 4 для индекса 3)
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
    # Читаем все строки из stdin, пока они есть
    for line in sys.stdin:
        # Убираем только \n в конце, оставляя отступы (важно для строк 4-5 в задаче 1)
        # Хотя для данной задачи rstrip() тоже сработает, rstrip('\n') безопаснее
        cleaned_line = line.rstrip('\n')
        # Игнорируем пустые строки, если они вдруг появятся
        if cleaned_line:
            lines.append(cleaned_line)
    
    # Входные данные для второй задачи содержат "вставленные" строки
    # #############
    # #...........#
    # ###B#C#B#D###
    #   #D#C#B#A#  <- Вставка 1
    #   #D#B#A#C#  <- Вставка 2
    #   #A#D#C#A#
    #   #########
    #
    # Нам нужно их "вставить" в правильном порядке, если они есть.
    # Стандартный `solve` ожидает 5 или 7 строк. 
    # Если на входе 5 строк (Задача 1) - все хорошо.
    # Если на входе 7 строк (Задача 2) - все хорошо.
    
    # Проблема может возникнуть, если входные данные для задачи 2 
    # передаются в "сжатом" виде (как в Advent of Code), 
    # но судя по вашему примеру, вы передаете полный лабиринт (7 строк).
    
    # Дополнительная логика "вставки" строк (как в AoC 2021 Day 23 Part 2)
    # на случай, если входные данные для 4-уровневой задачи приходят 
    # в 5-строчном формате (что маловероятно, судя по вашему ТЗ).
    
    # `lines` уже содержит полный набор строк (5 или 7)
    
    if len(lines) == 5 and lines[3].strip().startswith('#A#D#C#A#'):
        # Это вход для Задачи 1, но он похож на "сжатый" вход Задачи 2
        # (т.е. нижний ряд из примера Задачи 2)
        # Проверяем, не нужно ли нам "расширить" его
        # В вашем ТЗ четко разделены 5-строчный и 7-строчный вводы,
        # поэтому эта логика здесь не нужна. `solve` сам разберется.
        pass

    # Если входные данные для Задачи 2 (глубина 4) приходят
    # в 5-строчном виде, их нужно "расширить"
    # Это стандартная логика для задачи Advent of Code 2021 Day 23
    
    # Проверяем, является ли это 5-строчным вводом *первой* части
    is_part_1_format = (len(lines) == 5 and lines[3].strip().startswith('#'))

    if is_part_1_format:
        # Это точно часть 1 (5 строк, 4-я строка начинается с #)
        # (Например, ###A#D#C#A#)
        pass # `solve` обработает 5 строк
    elif len(lines) == 7:
        # Это точно часть 2 (7 строк)
        pass # `solve` обработает 7 строк
    elif len(lines) == 5:
        # Это 5-строчный ввод, НО 4-я строка НЕ начинается с #
        # (Например, __#A#D#C#A#)
        # Это формат ввода из "Примера 1", который нужно "расширить" 
        # для "Примера 2"?
        
        # Судя по вашим двум запросам, вы просто меняете входные
        # данные. Код `solve` уже написан так, чтобы
        # обрабатывать 5 ИЛИ 7 строк.
        
        # Если бы нам дали 5 строк из Задачи 1 и сказали "реши Задачу 2",
        # нам бы пришлось вставить строки:
        if lines[2] == '###B#C#B#D###' and lines[3].strip() == '#A#D#C#A#':
            # Это вход из Примера 1. Если нам нужно решить Пример 2
            # (глубина 4) с этим входом, мы должны вставить строки.
            # НО по вашему ТЗ, для Примера 2 дается СВОЙ 7-строчный вход.
            
            # ...
            # Кажется, я усложняю. Ваш `solve` уже динамический.
            # `main` просто должен передать `lines` как есть.
            
            pass

    result = solve(lines)
    print(result)


if __name__ == "__main__":
    main()
