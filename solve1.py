import numpy as np
import argparse
import sys
from utils import Node
from queue import PriorityQueue
import time
import sqlite3

con = sqlite3.connect("states.db")
cur = con.cursor()

def main():
    ap = argparse.ArgumentParser(description="Solve n x n slide puzzles")
    ap.add_argument("-s", "--size", default=3, type = int, help = "Size of the puzzle")
    ap.add_argument("-i","--initial", nargs='+', type=int, required=True, help="Initial state of the puzzle")
    ap.add_argument("-g", "--goal", nargs='+', type=int, default=None, help="Goal state of the puzzle")
    args = ap.parse_args()


    if not 3 <= args.size <= 5:
        sys.exit("Size of the puzzle must be between 3 and 5")
    if not validate_input(args.initial, args.size):
        sys.exit("Initial state is not valid")
    if args.goal:
        if not validate_input(args.goal, args.size):
            sys.exit("Goal state is not valid")

    size = args.size
    initial = args.initial
    goal = args.goal if args.goal else goal_state(size)
    cur.execute(f"CREATE TABLE IF NOT EXISTS x{size} (state VARCHAR(50) UNIQUE, solution VARCHAR(1000))")

    start_time = time.process_time()
    if solvability(initial, size):
        str_state = state_to_str(initial)
        if size == 3:
            cur.execute("SELECT solution FROM x3 WHERE state = ?", (str_state,))
        elif size == 4:
            cur.execute("SELECT solution FROM x4 WHERE state = ?", (str_state,))
        elif size == 5:
            cur.execute("SELECT solution FROM x5 WHERE state = ?", (str_state,))
        res = cur.fetchall()
        if len(res) == 0:
            solution = solve(initial, goal, size)
            path = solution[0]
            if solution[0] is not None:
                add_to_db(initial, path, size)
            total_duration = np.round(time.process_time() - start_time, 4)
            print_result(initial, path, size, total_duration)
        elif len(res) == 1:
            path = res[0][0].split("-")
            print_result(initial, path, size, None)
        else:
            sys.exit("Database is corrupted")
    else:
        sys.exit("Initial state is not solvable")



def solve(state, goal, size):
    start = Node(state, None, None, 0, manhattan_distance(state, goal, size))
    frontier = PriorityQueue()
    frontier.put(start)
    explored = set()
    while True:
        if frontier.empty():
            return None
        node = frontier.get()
        explored.add(tuple(node.state)) 
        if node.state == goal:
            moves = []
            while node.parent is not None:
                moves.append(node.action)
                node = node.parent
            moves.reverse()
            return (moves, len(explored))
        for action in actions(node.state, goal, size):
            if node.depth >= 150:
                pass
            result_state = result(action, node.state, size)
            child = Node(result_state, node, action, depth = node.depth + 1, manhattan=manhattan_distance(result_state, goal, size))
            if tuple(child.state) not in explored and solvability(child.state, size):
                frontier.put(child)



def validate_input(lst, size):
    expected_set = set(range(size**2))
    if not set(lst) == expected_set:
        return False
    return True



def goal_state(size):
    lst = list(range(size**2))
    lst.pop(0)
    lst.append(0)
    return lst



def solvability(lst, size):
    inversions = 0
    x = 0
    for i in lst:
        x += 1
        for j in lst[x:]:
            if i > j and j != 0:
                inversions += 1
    lineFromB = ( ( pow(size, 2) - (lst.index(0) + 1) ) // size ) + 1
    if size % 2 == 1:
        if inversions % 2 == 0:
            return True
        else:
            return False
    else:
        if (lineFromB % 2 == 0 and inversions % 2 == 1) or (
            lineFromB % 2 == 1 and inversions % 2 == 0
        ):
            return True
        else:
            return False
        

def actions(state, goal, size):
    state_2d = np.array(state).reshape(size, size)
    pos_0 = np.where(state_2d == 0)
    row, col = pos_0[0], pos_0[1]
    directions = []
    if row != 0:
        directions.append("up")
    if row != state_2d.shape[0] - 1:
        directions.append("down")
    if col != 0:
        directions.append("left")
    if col != state_2d.shape[1] - 1:
        directions.append("right")

    manhattan_distances = []

    for direction in directions:
        manhattan_distances.append({"direction":direction, "distance":manhattan_distance(result(direction, state, size), goal, size)})
    return [item["direction"] for item in sorted(manhattan_distances, key=lambda x: x['distance'], reverse=True)]



def result(direction, state, size):
    state = np.array(state).reshape(size, size)
    zero_pos = np.array(np.where(state == 0)).flatten()

    if direction == "up":
        state[zero_pos[0], zero_pos[1]], state[zero_pos[0] - 1, zero_pos[1]] = (
            state[zero_pos[0] - 1, zero_pos[1]],
            state[zero_pos[0], zero_pos[1]],
        )
        return state.flatten().tolist()

    if direction == "left":
        state[zero_pos[0], zero_pos[1]], state[zero_pos[0], zero_pos[1] - 1] = (
            state[zero_pos[0], zero_pos[1] - 1],
            state[zero_pos[0], zero_pos[1]],
        )
        return state.flatten().tolist()
    if direction == "right":
        state[zero_pos[0], zero_pos[1]], state[zero_pos[0], zero_pos[1] + 1] = (
            state[zero_pos[0], zero_pos[1] + 1],
            state[zero_pos[0], zero_pos[1]],
        )
        return state.flatten().tolist()

    if direction == "down":
        state[zero_pos[0], zero_pos[1]], state[zero_pos[0] + 1, zero_pos[1]] = (
            state[zero_pos[0] + 1, zero_pos[1]],
            state[zero_pos[0], zero_pos[1]],
        )
        return state.flatten().tolist()

        

def manhattan_distance(current, goal, size):
    current = np.array(current).reshape(size, size)
    goal = np.array(goal).reshape(size, size)
    manhattan_distance = 0
    for num in range(1, size**2):
        pos_current = np.array(np.where(current == num)).flatten()
        pos_final = np.array(np.where(goal == num)).flatten()
        manhattan_distance += np.sum(np.abs(pos_final - pos_current))
    return manhattan_distance



def print_puzzle_state(state, size):
    for row in range(size):
        for col in range(size):
            value = state[row * size + col]
            if value == 0:
                print(" ", end=" " if size == 3 else "  ")
            else:
                if size == 3:
                    print(value, end=" ")
                else:
                    print(value if value > 9 else f" {value}", end="  ")
        print()
    print()



def print_result(initial, path, size, time):
    print("Initial state:")
    print_puzzle_state(initial, size)
    prev_state = initial
    for action in path:
        print(f"Move empty slot {action.upper()}")
        current_state = result(action, prev_state, size)
        print_puzzle_state(current_state, size)
        prev_state = current_state
    print(f"Reached to goal state in {len(path)} moves,", f"took {time} seconds to solve" if time is not None else "solution found in database", end="\n\n")



def add_to_db(initial, path, size):
    str_state = state_to_str(initial)
    str_solution = "-".join(path)
    cur.execute(f"INSERT INTO x{size} (state, solution) VALUES (?, ?)", (str_state, str_solution))
    con.commit()
    prev_state = initial
    for i in range(len(path) - 1):
        state = result(path[i], prev_state, size)
        str_state = state_to_str(state)
        str_solution = "-".join(path[:i+1])
        cur.execute(f"INSERT OR IGNORE INTO x{size} (state, solution) VALUES (?, ?)", (str_state, str_solution))
        con.commit()
        prev_state = state

def state_to_str(initial):
    str_state = ""
    for i in initial:
        str_state += str(i) + "-"
    str_state = str_state[:-1]
    return str_state


if __name__ == "__main__":
    main()