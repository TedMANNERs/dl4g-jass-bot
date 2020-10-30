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
        MAX_POINTS = 157
        # normalize points since mcts expects payoffs between 1 and 0
        normalized_points = self.game_state.points / MAX_POINTS
        self.accumulated_payoff = normalized_points

    def update_wins(self):
        if self.game_state.points >= 79:
            self.wins += 1
