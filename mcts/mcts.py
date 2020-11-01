import numpy as np

from jass.game.game_observation import GameObservation
from jass.game.game_state import GameState
from jass.game.rule_schieber import RuleSchieber
from jass.game.game_sim import GameSim
from jass.game.const import *
from mcts.node import Node
from mcts.turn_action import TurnAction


class MonteCarloTreeSearch:
    def __init__(self, obs: GameObservation, rule: RuleSchieber, turn_action: TurnAction):
        self.obs = obs
        self.root = Node()
        self._rule = rule
        self._turn_action = turn_action
        self._exploration_weight = 1

    def get_best_node_from_simulation(self):
        hands = self._sample()
        selected_node = self._select_next_node()
        expanded_node = self._expand_node(selected_node, hands)
        if not expanded_node == selected_node:
            # Game has not ended ended so we need to simulate
            expanded_node = self._simulate(expanded_node, hands)
        self._backpropagate(expanded_node)

        # return node with the highest payoff
        return self.root.children[np.argmax([c.accumulated_payoff for c in self.root.children])]

    def _sample(self):
        # calculate which cards are still in the hands of players
        pre_hack_played_cards = np.concatenate([t for t in self.obs.tricks])
        # use ugly hack because tricks contain -1 for unplayed cards
        played_cards = pre_hack_played_cards[pre_hack_played_cards != -1]

        unplayed_cards = np.ones(36)
        for c in played_cards:
            unplayed_cards[c] = 0

        other_player_cards = unplayed_cards - self.obs.hand

        hands = np.zeros(shape=[4, 36])
        for player in range(MAX_PLAYER + 1):
            if player == self.obs.player:
                hands[player] = self.obs.hand
            else:
                hands[player], other_player_cards = self._get_random_hand(other_player_cards, player)
        print(other_player_cards)
        return hands

    def _get_random_hand(self, other_player_cards, player):
        # use ugly hack because current_trick contains -1 for unplayed cards
        current_trick_cards = self.obs.current_trick[self.obs.current_trick != -1]
        nr_of_previous_players_with_less_cards = len(current_trick_cards)

        previous_player = [1, 2, 3, 0]

        # all players ahead of us receive the same number of cards
        nr_of_cards_to_receive = len(np.flatnonzero(self.obs.hand))

        # all previous players receive one less
        previous_p = self.obs.player
        for x in range(nr_of_previous_players_with_less_cards):
            previous_p = previous_player[previous_p]
            if previous_p == player:
                # 1 less card because they already played a card
                nr_of_cards_to_receive -= 1

        # Choose random cards from other_player_cards
        hand_to_receive = np.zeros(36)
        cards_to_receive = np.random.choice(np.flatnonzero(other_player_cards), nr_of_cards_to_receive, replace=False)
        for card in cards_to_receive:
            hand_to_receive[card] = 1
            # remove the cards from other_player_cards so the next player cannot receive the same cards
            other_player_cards[card] = 0

        return hand_to_receive, other_player_cards

    def _select_next_node(self):
        node = self.root
        while node.isExpanded:  # TODO: Check if node is fully expanded?
            node = self._get_next_ucb1_child(node)
        return node

    def _expand_node(self, node: Node, hands):
        if node.state is None:
            root_sim = GameSim(self._rule)
            root_sim.init_from_cards(hands, self.obs.dealer)
            root_sim.state.trump = self.obs.trump
            node.state = root_sim.state

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
