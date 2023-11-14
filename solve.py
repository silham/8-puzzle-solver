import numpy as np
import sys

steps = 0


def main():
    s = 3
    intLst = []
    if sys.argv.__contains__("-s"):
        s_index = sys.argv.index("-s") + 1
        try:
            s = int(sys.argv[s_index])
        except (IndexError, ValueError):
            sys.exit("Something went wrong with arguments")
        else:
            if not (3 <= s <= 10):
                sys.exit("puzzle must be between 3x3 and 10x10")

    while True:
        if sys.argv.__contains__("-is"):
            is_index = sys.argv.index("-is") + 1
            try:
                inputLst = sys.argv[is_index : (is_index + s * s)]
            except (IndexError, ValueError):
                sys.exit("Something went wrong with arguments")
        else:
            inputLst = input("Initial state: ").strip().split(" ")

        if len(inputLst) == s * s:
            try:
                intLst = list(map(int, inputLst))
                validate_input(intLst, s)
                break
            except ValueError:
                pass
        else:
            pass

    initial = np.array(intLst).reshape(s, s)
    goal = goal_state(s)
    if solvability(intLst, s):
        solve({"state": initial, "prev_move": None}, goal, s)
    else:
        sys.exit("This puzzle is not solvable")


def validate_input(lst, size):
    expected_set = set(range(size**2))
    if not set(lst) == expected_set:
        sys.exit("Please recheck your input.")


def goal_state(size):
    lst = list(range(size**2))
    lst.pop(0)
    lst.append(0)
    return np.array(lst).reshape(size, size)


def solvability(lst, size):
    inversions = 0
    x = 0
    for i in lst:
        x += 1
        for j in lst[x:]:
            if i > j and j != 0:
                inversions += 1
    lineFromB = (pow(size, 2) - (lst.index(0) + 1)) // size
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


def misplaced_items(current, goal):
    comparison = current != goal
    misplaced_items = np.count_nonzero(comparison)
    return misplaced_items


def solve(current, goal, size):
    steps += 1
    directions = find_directions(current["state"], current["prev_move"])
    print(directions)
    distances = []
    possible_moves = make_moves(directions, current["state"])
    for move in possible_moves:
        distance = manhattan_distance(move["state"], goal, size)
        distances.append(distance)
    min_distance = min(distances)
    min_distances = [i for i in distances if i == min_distance]
    min_distance_states = []
    for distance in min_distances:
        state = possible_moves[min_distances.index(distance)]
        min_distance_states.append(state)
    print(min_distance_states)


def find_directions(arr, prev):
    result = np.where(arr == 0)
    row, col = result[0], result[1]
    directions = []
    if row != 0 and prev != "down":
        directions.append("up")
    if row != arr.shape[0] - 1 and prev != "up":
        directions.append("down")
    if col != 0 and prev != "right":
        directions.append("left")
    if col != arr.shape[1] - 1 and prev != "left":
        directions.append("right")

    return directions


def make_moves(directions, state):
    zero_pos = np.array(np.where(state == 0)).flatten()
    moved_states = []

    for direction in directions:
        current = np.array(state)
        if direction == "up":
            current[zero_pos[0], zero_pos[1]], current[zero_pos[0] - 1, zero_pos[1]] = (
                current[zero_pos[0] - 1, zero_pos[1]],
                current[zero_pos[0], zero_pos[1]],
            )
            moved_states.append({"state": current, "prev_move": "up"})

        if direction == "left":
            current[zero_pos[0], zero_pos[1]], current[zero_pos[0], zero_pos[1] - 1] = (
                current[zero_pos[0], zero_pos[1] - 1],
                current[zero_pos[0], zero_pos[1]],
            )
            moved_states.append({"state": current, "prev_move": "left"})

        if direction == "right":
            current[zero_pos[0], zero_pos[1]], current[zero_pos[0], zero_pos[1] + 1] = (
                current[zero_pos[0], zero_pos[1] + 1],
                current[zero_pos[0], zero_pos[1]],
            )
            moved_states.append({"state": current, "prev_move": "right"})

        if direction == "down":
            current[zero_pos[0], zero_pos[1]], current[zero_pos[0] + 1, zero_pos[1]] = (
                current[zero_pos[0] + 1, zero_pos[1]],
                current[zero_pos[0], zero_pos[1]],
            )
            moved_states.append({"state": current, "prev_move": "down"})
    return moved_states


def manhattan_distance(current, goal, size):
    manhattan_distance = 0
    for num in range(1, size**2):
        pos_current = np.array(np.where(current == num)).flatten()
        pos_final = np.array(np.where(goal == num)).flatten()
        manhattan_distance += np.sum(np.abs(pos_final - pos_current))
    return manhattan_distance


if __name__ == "__main__":
    main()
