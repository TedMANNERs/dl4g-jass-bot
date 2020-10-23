import numpy as np
from jass.game.game_state import GameState
from mcts.node import Node



class MonteCarloTreeSearch:
    def __init__(self, current_trick):
        self.root = Node(None)
        node = self.root
        for card in current_trick:
            node.children.append(Node(card))

        self._exploration_weight = 1

    def get_best_node_from_simulation(self, valid_cards, state: GameState):
        leaf_node = self._select_next_node()
        self._expand_node(leaf_node, valid_cards)
        payoff = self._simulate(leaf_node, state)
        self._backpropagate(leaf_node.get_path(), payoff)
        pass

    def _select_next_node(self):
        node = self.root
        while len(node.children) > 0 or not node.isExpanded:
            # TODO: Do we need to select unexplored nodes only?
            node = self.get_next_ucb1_child(node)
        return node

    def _expand_node(self, node, valid_cards):
        # TODO: Do we need check if the game ends?
        for card in valid_cards:
            child_node = Node(card)
            child_node.parent = node
            node.children.append(child_node)
        node.isExpanded = True

    def _simulate(self, leaf_node, state: GameState):
        nr_played_cards = len(leaf_node.get_path())
        if nr_played_cards >= 36:
            my_points = state.points

    def _backpropagate(self, param, payoff):
        raise NotImplementedError()

    def get_next_ucb1_child(self, node):
        max_ucb_child = node
        for child in node.children:
            exploration = self._exploration_weight * np.sqrt(np.log(self.root.visit_count) / node.visit_count)
            child.ucb = node.wins / node.visit_count + exploration
            if child.ucb > max_ucb_child.ucb:
                max_ucb_child = child
        return max_ucb_child
