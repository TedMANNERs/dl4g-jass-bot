import numpy as np


class Node:
    def __init__(self, card):
        self.card = card
        self.parent = None
        self.children = []
        self.simulation_count = 0
        self.accumulated_payoff = np.zeros([4])
        self.ucb = 0

    def get_path(self):
        path = [self]
        node = self
        while node.parent is not None:
            node = node.parent
            path.append(node)
        return path
