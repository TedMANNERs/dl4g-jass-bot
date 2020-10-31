from jass.game.game_observation import GameObservation


class Node:
    def __init__(self, obs: GameObservation, parent=None, card=None):
        self.obs = obs
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

    def calculate_payoff(self, sim_obs: GameObservation):
        MAX_POINTS = 157
        my_team_points = self._get_team_points(sim_obs)
        # normalize points since mcts expects payoffs between 1 and 0
        normalized_points = my_team_points / MAX_POINTS
        self.accumulated_payoff = normalized_points

    def update_wins(self, sim_obs: GameObservation):
        my_team_points = self._get_team_points(sim_obs)
        if my_team_points >= 79:  # More than half of the points
            self.wins += 1

    def _get_team_points(self, sim_obs: GameObservation):
        team_index = 0
        if sim_obs.player % 2 != 0:  # Player 0 and 2
            team_index = 1
        return sim_obs.points[team_index]
