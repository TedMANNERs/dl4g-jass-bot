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
        return self.root.children[np.argmax([c.accumulated_payoff for c in self.root.children])]

    def _select_next_node(self):
        node = self.root
        while len(node.children) > 0:  # TODO: Check if node is fully expanded?
            node = self._get_next_ucb1_child(node)
        return node

    # TODO: Expand fully, meaning all possible children
    def _expand_node(self, node: Node):
        if self._is_round_finished(node.game_state):
            new_game_state = self._play_single_turn(node.game_state)
            child_node = Node(new_game_state, node)
            return child_node
        else:
            return node

    def _simulate(self, leaf_node: Node):
        # nr_played_cards = len(leaf_node.get_path())
        sim_game_state = leaf_node.game_state
        while self._is_round_finished(sim_game_state):
            # play a card
            sim_game_state = self._play_single_turn(sim_game_state)

        leaf_node.calculate_payoff(sim_game_state)
        leaf_node.update_wins(sim_game_state)
        return leaf_node

    def _backpropagate(self, node: Node):
        current_node = node
        while current_node.parent is not None:
            current_node.parent.accumulated_payoff += current_node.accumulated_payoff
            current_node = current_node.parent
            current_node.visit_count += 1
        current_node.visit_count += 1

    def _play_single_turn(self, game_state: GameState):
        simulation = GameSim(self._rule)
        simulation.init_from_state(game_state)

        # Get valid cards of players hand
        all_valid_cards = self._rule.get_valid_cards_from_state(game_state)
        valid_cards = all_valid_cards * game_state.hands[game_state.player]
        random_valid_card = np.random.choice(np.flatnonzero(valid_cards))  # TODO: Use rules here?
        simulation.action_play_card(random_valid_card)
        return simulation.state

    def _get_next_ucb1_child(self, node: Node):
        max_ucb_child = node
        for child in node.children:
            exploration = self._exploration_weight * np.sqrt(np.log(self.root.visit_count) / node.visit_count)
            child.ucb = node.wins / node.visit_count + exploration
            if child.ucb > max_ucb_child.ucb:
                max_ucb_child = child
        return max_ucb_child

    def _is_round_finished(self, game_state: GameState):
        return game_state.nr_played_cards < 36
