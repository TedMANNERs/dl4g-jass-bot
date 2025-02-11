import numpy as np
from jass.game.game_state import GameState
from jass.game.rule_schieber import RuleSchieber
from jass.game.game_sim import GameSim
from jass.game.const import *
from jass.agent_actions.actions import get_best_card_using_simple_rules_from_state
from mcts.cheating_node import Node
from mcts.cheating_turn_action import TurnAction


class MonteCarloTreeSearch:
    def __init__(self, state: GameState, rule: RuleSchieber, turn_action: TurnAction):
        self.root = Node(state)
        self._rule = rule
        self.turn_action = turn_action
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
        while node.isExpanded:  # TODO: Check if node is fully expanded?
            node = self._get_next_ucb1_child(node)
        return node

    def _expand_node(self, node: Node):
        if self._is_round_finished(node.game_state):
            turns = self._play_all_possible_turns(node.game_state)
            child_nodes = [Node(turn[0], node, turn[1]) for turn in turns]
            node.isExpanded = True
            return np.random.choice(child_nodes)  # Choose random child state TODO: Use rules here?
        else:
            return node

    def _simulate(self, leaf_node: Node):
        # nr_played_cards = len(leaf_node.get_path())
        sim_game_state = leaf_node.game_state
        while self._is_round_finished(sim_game_state):
            # play a card
            sim_game_state = self.turn_action.play_single_turn(sim_game_state, self._rule)

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

    def _play_all_possible_turns(self, game_state: GameState):
        # Get valid cards of players hand
        valid_cards = self._rule.get_valid_cards_from_state(game_state)

        turns = []
        for card in np.flatnonzero(valid_cards):
            simulation = GameSim(self._rule)
            simulation.init_from_state(game_state)
            simulation.action_play_card(card)
            turns.append([simulation.state, card])

        return turns

    def _get_next_ucb1_child(self, node: Node):
        max_ucb = 0
        max_ucb_child = node
        for child in node.children:
            exploration = self._exploration_weight * np.sqrt(np.log(self.root.visit_count) / node.visit_count)
            child_ucb = node.wins / node.visit_count + exploration
            if child_ucb > max_ucb:
                max_ucb = child_ucb
                max_ucb_child = child

        return max_ucb_child

    def _is_round_finished(self, game_state: GameState):
        return game_state.nr_played_cards < 36
