import numpy as np

from jass.game.game_observation import GameObservation
from jass.game.game_state import GameState
from jass.game.game_state_util import state_from_observation, observation_from_state
from jass.game.rule_schieber import RuleSchieber
from jass.game.game_sim import GameSim
from jass.game.const import *
from mcts.node import Node
from mcts.sampler import Sampler
from mcts.turn_action import TurnAction


# WITH INFORMATION SETS
class MonteCarloTreeSearch:
    def __init__(self, obs: GameObservation, rule: RuleSchieber, turn_action: TurnAction):
        self.obs = obs
        self._sampler = Sampler()
        self.root = Node(obs.hand)
        self._rule = rule
        self._turn_action = turn_action
        self._exploration_weight = 1

    def get_best_node_from_simulation(self):
        # game state is kept outside of the information set node and updated while selecting and expanding
        hands = self._sampler.get_random_sample(self.obs)
        game_state = state_from_observation(self.obs, hands)

        print("SELECTION")
        selected_node, game_state = self._select_next_node(game_state)
        expanded_node = self._expand_node(selected_node, game_state)
        if not expanded_node == selected_node:
            # Game has not ended ended so we need to simulate
            expanded_node = self._simulate(expanded_node, game_state)
        self._backpropagate(expanded_node)

        # return node with the highest payoff
        return self.root.children[np.argmax([c.accumulated_payoff for c in self.root.children])]

    def _select_next_node(self, game_state: GameState):
        node = self.root
        while node.isExpanded:
            print(node.card)
            valid_cards = self._rule.get_valid_cards_from_state(game_state)
            best_node = self._get_next_ucb1_child(node, valid_cards)
            if best_node == node:
                break

            node = best_node
            game_state = self._play_card(game_state, node.card) # update game state while selecting
        return node, game_state

    def _expand_node(self, node: Node, game_state: GameState):
        if not self._is_round_finished(game_state.nr_played_cards):
            turns = self._play_all_possible_cards(game_state)
            child_nodes = []
            for t in turns:
                state = t[0]
                my_hand = state.hands[state.player]
                child_nodes.append(Node(my_hand, parent=node, card=t[1]))
            node.isExpanded = True
            return np.random.choice(child_nodes)  # Choose random child state TODO: Use rules here?
        else:
            return node

    def _simulate(self, leaf_node: Node, game_state: GameState):
        sim_state = game_state
        while not self._is_round_finished(sim_state.nr_played_cards):
            # play a card
            sim_state = self._turn_action.play_single_turn(sim_state, self._rule)

        leaf_node.calculate_payoff(sim_state.player, sim_state.points)
        leaf_node.update_wins(sim_state.player, sim_state.points)
        return leaf_node

    def _backpropagate(self, node: Node):
        current_node = node
        while current_node.parent is not None:
            current_node.parent.accumulated_payoff += current_node.accumulated_payoff
            current_node = current_node.parent
            current_node.visit_count += 1
        current_node.visit_count += 1

    def _play_card(self, game_state: GameState, card) -> GameState:
        simulation = GameSim(self._rule)
        simulation.init_from_state(game_state)
        simulation.action_play_card(card)
        return simulation.state

    def _play_all_possible_cards(self, game_state: GameState):
        valid_cards = self._rule.get_valid_cards_from_state(game_state)
        turns = []
        for card in np.flatnonzero(valid_cards):
            state = self._play_card(game_state, card)
            turns.append([state, card])
        return turns

    def _get_next_ucb1_child(self, node: Node, valid_cards_for_node):
        max_ucb = 0
        max_ucb_child = node
        for child in node.children:
            if not child.is_compatible(valid_cards_for_node):
                continue
            exploration = self._exploration_weight * np.sqrt(np.log(node.visit_count) / child.visit_count)
            child_ucb = child.wins / child.visit_count + exploration
            if child_ucb > max_ucb:
                max_ucb = child_ucb
                max_ucb_child = child

        return max_ucb_child

    @staticmethod
    def _is_round_finished(nr_played_cards):
        return nr_played_cards >= 36
