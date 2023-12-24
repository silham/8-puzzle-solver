class Node:
    def __init__(self, state, parent, action, depth, manhattan):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth
        self.manhattan = manhattan

    def __lt__(self, other):
        return (self.depth + self.manhattan) < (other.depth + other.manhattan)    

