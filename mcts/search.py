from mcts.node import Node


class MonteCarloTreeSearch:
    def __init__(self, root_card):
        self.root = Node(root_card)

    def get_best_node_from_simulation(self, valid_cards):
        leaf_node = self._select_next_node(valid_cards)
        self._expand_node(leaf_node, valid_cards)
        payoff = self._simulate(leaf_node)
        self._backpropagate(leaf_node.get_path(), payoff)
        pass

    def _select_next_node(self, valid_cards):
        raise NotImplementedError()

    def _expand_node(self, leaf_node, valid_cards):
        raise NotImplementedError()

    def _simulate(self, leaf_node):
        raise NotImplementedError()

    def _backpropagate(self, param, payoff):
        raise NotImplementedError()
