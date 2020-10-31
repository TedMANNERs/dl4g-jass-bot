import numpy as np

from jass.game.game_observation import GameObservation
from jass.game.rule_schieber import RuleSchieber
from jass.game.game_sim import GameSim
from jass.game.const import *
from mcts.node import Node
from mcts.turn_action import TurnAction


class MonteCarloTreeSearch:
    def __init__(self, obs: GameObservation, rule: RuleSchieber, turn_action: TurnAction):
        self.root = Node(obs)
        self._rule = rule
        self._turn_action = turn_action
        self._exploration_weight = 1

    def get_best_node_from_simulation(self):
        hands = self._sample()
        selected_node = self._select_next_node()
        expanded_node = self._expand_node(selected_node)
        if not expanded_node == selected_node:
            # Game has not ended ended so we need to simulate
            expanded_node = self._simulate(expanded_node, hands)
        self._backpropagate(expanded_node)

        # return node with the highest payoff
        return self.root.children[np.argmax([c.accumulated_payoff for c in self.root.children])]


    def _sample(self):
        # calculate which cards are still in the hands of players
        played_cards = np.concatenate([t for t in self.root.obs.tricks])
        cards_in_play = np.ones(36)
        for c in played_cards:
            cards_in_play[c] = 0
        other_player_cards = cards_in_play - self.root.obs.current_trick - self.root.obs.hand

        MAX_CARDS_COUNT = 9
        my_card_count = len(np.flatnonzero(self.root.obs.hand))

        hands = np.zeros(shape=[4, 36])
        for player in range(MAX_PLAYER + 1):
            if player == self.root.obs.player:
                hands[player] = self.root.obs.hand
            else:
                hands[player], other_player_cards = self._get_random_hand(other_player_cards, player)
        return hands

    def _get_random_hand(self, other_player_cards, player):
         1 2 3 4
           x
         c
        nr_of_next_players_with_more_cards = 3 - len(self.root.obs.current_trick)
        # TODO: calculate
        # Choose random cards from other_player_cards
        nr_of_cards = len(np.flatnonzero(other_player_cards)) / 3
        return [], other_player_cards

    def _select_next_node(self):
        node = self.root
        while node.isExpanded:  # TODO: Check if node is fully expanded?
            node = self._get_next_ucb1_child(node)
        return node

    def _expand_node(self, node: Node):
        if self._is_round_finished(node.obs):
            turns = self._play_all_possible_turns(node.obs)
            child_nodes = [Node(turn[0], node, turn[1]) for turn in turns]
            node.isExpanded = True
            return np.random.choice(child_nodes)  # Choose random child state TODO: Use rules here?
        else:
            return node

    def _simulate(self, leaf_node: Node, hands):
        # nr_played_cards = len(leaf_node.get_path())
        sim_obs = leaf_node.obs
        while self._is_round_finished(sim_obs):
            # play a card
            sim_obs = self._turn_action.play_single_turn(hands, sim_obs, self._rule)

        leaf_node.calculate_payoff(sim_obs)
        leaf_node.update_wins(sim_obs)
        return leaf_node

    def _backpropagate(self, node: Node):
        current_node = node
        while current_node.parent is not None:
            current_node.parent.accumulated_payoff += current_node.accumulated_payoff
            current_node = current_node.parent
            current_node.visit_count += 1
        current_node.visit_count += 1

    def _play_all_possible_turns(self, obs: GameObservation):
        # Get valid cards of players hand
        valid_cards = self._rule.get_valid_cards_from_obs(obs)

        turns = []
        for card in np.flatnonzero(valid_cards):
            simulation = GameSim(self._rule)
            simulation.init_from_state(obs)
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

    def _is_round_finished(self, obs: GameObservation):
        return obs.nr_played_cards < 36
