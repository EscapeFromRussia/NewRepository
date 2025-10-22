#!/usr/bin/env python3
import sys
import heapq

COST = {
    'A': 1,
    'B': 10,
    'C': 100,
    'D': 1000
}

TARGET_ROOM_IDX = {
    'A': 0,
    'B': 1,
    'C': 2,
    'D': 3
}

ROOM_TARGET_TYPE = ['A', 'B', 'C', 'D']

PORTAL_POS = [2, 4, 6, 8]

STOP_POS = {0, 1, 3, 5, 7, 9, 10}

def solve(lines: list[str]) -> int:
    """
    Решение задачи о сортировке в лабиринте с использованием алгоритма Дейкстры.
    Работает для комнат глубиной 2 и 4.

    Args:
        lines: список строк, представляющих лабиринт

    Returns:
        минимальная энергия для достижения целевой конфигурации
    """

    if len(lines) == 5:
        room_depth = 2
    elif len(lines) == 7:
        room_depth = 4
    else:
        raise ValueError("Неподдерживаемый формат ввода: ожидалось 5 или 7 строк")

    initial_hallway = tuple(lines[1][1:12])
    
    room_cols = [3, 5, 7, 9]
    temp_rooms = [[] for _ in range(4)]
    
    for r_idx in range(room_depth):
        line = lines[2 + r_idx]
        for c_idx in range(4):
            col_pos = room_cols[c_idx]
            temp_rooms[c_idx].append(line[col_pos])
            
    initial_rooms = tuple(tuple(room) for room in temp_rooms)
    
    initial_state = (initial_hallway, initial_rooms)

    target_rooms = tuple(
        (ROOM_TARGET_TYPE[i],) * room_depth for i in range(4)
    )
    target_state = (
        ('.',) * 11,
        target_rooms
    )
    pq = [(0, initial_state)]
    
    min_costs = {initial_state: 0}

    while pq:
        cost, current_state = heapq.heappop(pq)
        hallway, rooms = current_state

        if current_state == target_state:
            return cost

        if cost > min_costs.get(current_state, float('inf')):
            continue

        for room_idx in range(4):
            room = rooms[room_idx]
            target_type = ROOM_TARGET_TYPE[room_idx]

            if all(amphipod == '.' or amphipod == target_type for amphipod in room):
                continue

            for depth_idx, amphipod_to_move in enumerate(room):
                if amphipod_to_move != '.':
                    steps_to_exit = depth_idx + 1
                    portal = PORTAL_POS[room_idx]
                    
                    for stop_pos in STOP_POS:
                        path_start = min(portal, stop_pos)
                        path_end = max(portal, stop_pos)
                        
                        if stop_pos < portal:
                            path_indices = range(stop_pos, portal)
                        else:
                            path_indices = range(portal + 1, stop_pos + 1)
                        
                        if all(hallway[i] == '.' for i in path_indices):
                            move_cost = (steps_to_exit + abs(stop_pos - portal)) * COST[amphipod_to_move]
                            new_total_cost = cost + move_cost

                            new_hallway = list(hallway)
                            new_hallway[stop_pos] = amphipod_to_move
                            
                            new_rooms = list(list(r) for r in rooms)
                            new_rooms[room_idx][depth_idx] = '.'
                            
                            new_state = (tuple(new_hallway), tuple(tuple(r) for r in new_rooms))

                            if new_total_cost < min_costs.get(new_state, float('inf')):
                                min_costs[new_state] = new_total_cost
                                heapq.heappush(pq, (new_total_cost, new_state))
                    
                    break 

        for hall_idx, amphipod in enumerate(hallway):
            if amphipod == '.':
                continue

            target_room_idx = TARGET_ROOM_IDX[amphipod]
            target_room = rooms[target_room_idx]
            portal = PORTAL_POS[target_room_idx]

            if not all(a == '.' or a == amphipod for a in target_room):
                continue

            if hall_idx < portal:
                path_indices = range(hall_idx + 1, portal + 1)
            else:
                path_indices = range(portal, hall_idx)

            if not all(hallway[i] == '.' for i in path_indices):
                continue 
            
            dest_depth = -1
            for d in range(room_depth - 1, -1, -1):
                if target_room[d] == '.':
                    dest_depth = d
                    break 
            
            if dest_depth == -1:
                continue

            hall_steps = abs(hall_idx - portal)
            room_steps = dest_depth + 1 
            move_cost = (hall_steps + room_steps) * COST[amphipod]
            new_total_cost = cost + move_cost

            new_hallway = list(hallway)
            new_hallway[hall_idx] = '.'
            
            new_rooms = list(list(r) for r in rooms)
            new_rooms[target_room_idx][dest_depth] = amphipod
            
            new_state = (tuple(new_hallway), tuple(tuple(r) for r in new_rooms))

            if new_total_cost < min_costs.get(new_state, float('inf')):
                min_costs[new_state] = new_total_cost
                heapq.heappush(pq, (new_total_cost, new_state))

    return -1


def main():
    lines = []
    for line in sys.stdin:
        cleaned_line = line.rstrip('\n')
        if cleaned_line:
            lines.append(cleaned_line)
    
    if len(lines) == 5 and lines[3].strip().startswith('#A#D#C#A#'):
        pass
    is_part_1_format = (len(lines) == 5 and lines[3].strip().startswith('#'))

    if is_part_1_format:
        pass 
    elif len(lines) == 7:
        pass 
    elif len(lines) == 5:
        if lines[2] == '###B#C#B#D###' and lines[3].strip() == '#A#D#C#A#':
            pass

    result = solve(lines)
    print(result)


if __name__ == "__main__":
    main()
