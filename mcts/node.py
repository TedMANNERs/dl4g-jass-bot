# Node = information set
class Node:
    def __init__(self, my_hand, hand_sizes, parent=None, card=None):
        self.my_hand = my_hand
        self.hand_sizes = hand_sizes
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

    def calculate_payoff(self, player, points):
        MAX_POINTS = 157
        my_team_points = self._get_team_points(player, points)
        # normalize points since mcts expects payoffs between 1 and 0
        normalized_points = my_team_points / MAX_POINTS
        self.accumulated_payoff = normalized_points

    def update_wins(self, player, points):
        my_team_points = self._get_team_points(player, points)
        if my_team_points >= 79:  # More than half of the points
            self.wins += 1

    def _get_team_points(self, player, points):
        team_index = 0
        if player % 2 != 0:  # Player 0 and 2
            team_index = 1
        return points[team_index]
