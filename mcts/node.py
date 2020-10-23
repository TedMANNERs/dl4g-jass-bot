import numpy as np


class Node:
    def __init__(self, card):
        self.card = card
        self.parent = None
        self.children = []
        self.isExpanded = False
        self.visit_count = 0
        self.wins = 0
        self.accumulated_payoff = 0
        self.enemy_accumulated_payoff = 0
        self.ucb = 0

    def get_path(self):
        path = [self]
        node = self
        while node.parent is not None:
            node = node.parent
            path.append(node)
        return path
