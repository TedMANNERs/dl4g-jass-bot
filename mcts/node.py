from jass.game.game_state import GameState


class Node:
    def __init__(self, game_state: GameState, parent = None):
        self.game_state = game_state
        self.parent = parent
        self.children = []
        self.isExpanded = False
        self.visit_count = 0
        self.wins = 0
        self.accumulated_payoff = 0
        self.ucb = 0

    def get_path(self):
        path = [self]
        node = self
        while node.parent is not None:
            node = node.parent
            path.append(node)
        return path

    def calculate_payoff(self):
        points = self.game_state.points
        if points >= 79: # More than half of all possible points
            self.accumulated_payoff = 1
            self.wins += 1
        else:
            self.accumulated_payoff = 0
