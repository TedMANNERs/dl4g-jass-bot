from jass.game.game_state import GameState


class Node:
    def __init__(self, game_state: GameState, parent=None, card=None):
        self.game_state = game_state
        self.parent = parent
        self.children = []
        self.card = card
        self.isExpanded = False
        self.visit_count = 1
        self.wins = 0
        self.accumulated_payoff = 0

        if self.parent is not None:
            self.parent.children.append(self)

    def get_path(self):
        path = [self]
        node = self
        while node.parent is not None:
            node = node.parent
            path.append(node)
        return path

    def calculate_payoff(self, sim_game_state: GameState):
        MAX_POINTS = 157
        my_team_points = self._get_team_points(sim_game_state)
        # normalize points since mcts expects payoffs between 1 and 0
        normalized_points = my_team_points / MAX_POINTS
        self.accumulated_payoff = normalized_points

    def update_wins(self, sim_game_state: GameState):
        my_team_points = self._get_team_points(sim_game_state)
        if my_team_points >= 79:  # More than half of the points
            self.wins += 1

    def _get_team_points(self, sim_game_state: GameState):
        team_index = 0
        if sim_game_state.player % 2 != 0:  # Player 0 and 2
            team_index = 1
        return sim_game_state.points[team_index]
