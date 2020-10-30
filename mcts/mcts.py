import numpy as np
from jass.game.game_state import GameState
from jass.game.rule_schieber import RuleSchieber
from jass.game.game_sim import GameSim
from jass.game.const import *
from mcts.node import Node
import sys


class MonteCarloTreeSearch:
    def __init__(self, state: GameState, rule: RuleSchieber):
        self.root = Node(state)
        self._rule = rule
        self._exploration_weight = 1

    def get_best_node_from_simulation(self):
        selected_node = self._select_next_node()
        expanded_node = self._expand_node(selected_node)
        if not expanded_node == selected_node:
            # Game has not ended ended so we need to simulate
            expanded_node = self._simulate(expanded_node)
        self._backpropagate(expanded_node)

        # return node with the highest payoff
        return max(c.accumulated_payoff for c in self.root.children)

    def _select_next_node(self):
        node = self.root
        while len(node.children) > 0 or not node.isExpanded:
            node = self.get_next_ucb1_child(node)
        return node

    def _expand_node(self, node: Node):
        if self.is_round_finished(node):
            child_node = self._play_single_turn(node)
            node.isExpanded = True
            return child_node
        else:
            return node

    def _simulate(self, leaf_node: Node):
        # nr_played_cards = len(leaf_node.get_path())
        current_node = leaf_node
        while self.is_round_finished(current_node):
            # play a card
            new_child_node = self._play_single_turn(current_node)
            current_node = new_child_node

        current_node.calculate_payoff()
        current_node.update_wins()
        return current_node

    def _backpropagate(self, node: Node):
        current_node = node
        current_node.visit_count += 1
        while current_node.parent is not None:
            current_node.parent.accumulated_payoff += current_node.accumulated_payoff
            current_node = current_node.parent

    def _play_single_turn(self, node: Node):
        simulation = GameSim(self._rule)
        simulation.init_from_state(node.game_state)

        # Play a card from all players valid cards, since we play for them too
        possible_cards = self._get_valid_cards_from_all_hands(node.game_state)
        random_valid_card = np.random.choice(possible_cards, 1)  # TODO: Use rules here?
        simulation.action_play_card(random_valid_card)
        child_node = Node(simulation.state, node)  # TODO: Is a new node always needed, what if we revisit it?
        node.children.append(child_node)
        return child_node

    def _get_valid_cards_from_all_hands(self, state: GameState):
        return self._rule.get_valid_cards(hand=np.sum(state.hands, axis=0),
                                          current_trick=state.current_trick,
                                          move_nr=state.nr_cards_in_trick,
                                          trump=state.trump)

    def get_next_ucb1_child(self, node: Node):
        if node.visit_count == 0:
            node.visit_count = sys.maxsize

        max_ucb_child = node
        for child in node.children:
            exploration = self._exploration_weight * np.sqrt(np.log(self.root.visit_count) / node.visit_count)
            child.ucb = node.wins / node.visit_count + exploration
            if child.ucb > max_ucb_child.ucb:
                max_ucb_child = child
        return max_ucb_child

    def is_round_finished(self, node: Node):
        return node.game_state.nr_played_cards < 36
