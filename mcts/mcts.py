import numpy as np

from jass.game.game_observation import GameObservation
from jass.game.game_state import GameState
from jass.game.rule_schieber import RuleSchieber
from jass.game.game_sim import GameSim
from jass.game.const import *
from mcts.node import Node
from mcts.sampler import Sampler
from mcts.turn_action import TurnAction


class MonteCarloTreeSearch:
    def __init__(self, obs: GameObservation, rule: RuleSchieber, turn_action: TurnAction):
        self.obs = obs
        root_states = self._get_root_states(obs)
        self.root = Node(root_states)
        self._rule = rule
        self._turn_action = turn_action
        self._exploration_weight = 1
        self._sampler = Sampler(obs)

    def _get_root_states(self, obs: GameObservation):
        possible_hands = self._sampler.get_all_samples()
        root_states = []
        for hands in possible_hands:
            state = GameState()
            self.dealer = obs.dealer
            self.player = obs.player
            self.trump = obs.trump
            self.forehand = obs.forehand
            self.declared_trump = obs.declared_trump
            self.hands = hands
            self.tricks = obs.tricks
            self.trick_winner = obs.trick_winner
            self.trick_points = obs.trick_points
            self.trick_first_player = obs.trick_first_player
            self.current_trick = obs.current_trick
            self.nr_tricks = obs.nr_tricks
            self.nr_cards_in_trick = 0
            self.nr_played_cards = 0
            self.points = obs.points
            root_states.append(state)
        return root_states

    def get_best_node_from_simulation(self):
        hands = self._sampler.get_random_sample()
        selected_node = self._select_next_node()
        expanded_node = self._expand_node(selected_node, hands)
        if not expanded_node == selected_node:
            # Game has not ended ended so we need to simulate
            expanded_node = self._simulate(expanded_node, hands)
        self._backpropagate(expanded_node)

        # return node with the highest payoff
        return self.root.children[np.argmax([c.accumulated_payoff for c in self.root.children])]



    def _select_next_node(self):
        node = self.root
        while node.isExpanded:  # TODO: Check if node is fully expanded?
            node = self._get_next_ucb1_child(node)
        return node

    def _expand_node(self, node: Node, hands):
        if self._is_round_finished(node.state):
            turns = self._play_all_possible_turns(node.state, hands)
            child_nodes = [Node(turn[0], node, turn[1]) for turn in turns]
            node.isExpanded = True
            return np.random.choice(child_nodes)  # Choose random child state TODO: Use rules here?
        else:
            return node

    def _simulate(self, leaf_node: Node, hands):
        # nr_played_cards = len(leaf_node.get_path())
        sim_state = leaf_node.state
        while self._is_round_finished(sim_state):
            # play a card
            sim_state = self._turn_action.play_single_turn(hands, sim_state, self._rule)

        leaf_node.calculate_payoff(sim_state)
        leaf_node.update_wins(sim_state)
        return leaf_node

    def _backpropagate(self, node: Node):
        current_node = node
        while current_node.parent is not None:
            current_node.parent.accumulated_payoff += current_node.accumulated_payoff
            current_node = current_node.parent
            current_node.visit_count += 1
        current_node.visit_count += 1

    def _play_all_possible_turns(self, state: GameState, hands):
        # Get valid cards of players hand
        valid_cards = self._rule.get_valid_cards_from_state(state)

        turns = []
        for card in np.flatnonzero(valid_cards):
            simulation = GameSim(self._rule)
            simulation.init_from_state(state)
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

    def _is_round_finished(self, state: GameState):
        return state.nr_played_cards < 36
