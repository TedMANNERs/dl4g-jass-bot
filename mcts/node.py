from jass.game.game_state import GameState


class Node:
    def __init__(self, game_state: GameState, parent=None):
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
        my_team_points = self._get_team_points()
        # normalize points since mcts expects payoffs between 1 and 0
        normalized_points = my_team_points / MAX_POINTS
        self.accumulated_payoff = normalized_points

    def update_wins(self):
        my_team_points = self._get_team_points()
        if my_team_points >= 79:
            self.wins += 1

    def _get_team_points(self):
        team_index = 0
        if self.game_state.player % 2 != 0:  # Player 0 and 2
            team_index = 1
        return self.game_state.points[team_index]
