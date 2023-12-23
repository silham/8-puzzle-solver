import numpy as np

class Node:
    def __init__(self, state, parent, action, depth, manhattan):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth
        self.manhattan = manhattan

    def __lt__(self, other):
        return (self.depth + self.manhattan) < (other.depth + other.manhattan)    

class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(np.array_equal(node.state, state) for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node