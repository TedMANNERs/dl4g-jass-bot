import time
import logging
import numpy as np
from jass.agents.agent import CheatingAgent
from jass.game.game_state import GameState
from jass.game.rule_schieber import RuleSchieber
from jass.game.const import *
from mcts.search import MonteCarloTreeSearch
from jass.agent_actions.actions import *


class AgentCheatingMonteCarlo (CheatingAgent):
    """
    Agent to act as a player in a match of jass.
    """
    def __init__(self, simulation_time):
        self.simulation_time = simulation_time
        # log actions
        self._logger = logging.getLogger(__name__)
        # Use rule object to determine valid actions
        self._rule = RuleSchieber()
        # init random number generator
        self._rng = np.random.default_rng()
        self.search_tree = None

    def action_trump(self, state: GameState) -> int:
        """
        Determine trump action for the given observation
        Args:
            state: the game state, it must be in a state for trump selection

        Returns:
            selected trump as encoded in jass.match.const or jass.match.const.PUSH
        """
        self._logger.info('Trump request')
        result = select_trump(state.hands[state.player], state.forehand)
        self._logger.info('Result: {}'.format(result))
        return result

    def action_play_card(self, state: GameState) -> int:
        """
        Determine the card to play.

        Args:
            state: the game state

        Returns:
            the card to play, int encoded as defined in jass.match.const
        """
        if state.nr_tricks <= 0:
            self.search_tree = MonteCarloTreeSearch(state.current_trick)

        valid_cards = self._rule.get_valid_cards_from_state(state)

        node = self.search_tree.get_best_node_from_simulation(valid_cards, state)
        start_time = time.time()
        while time.time() - start_time <= self.simulation_time:
            node = self.search_tree.get_best_node_from_simulation(valid_cards, state)

        card = node.card
        self._logger.info('Played card: {}'.format(card_strings[card]))
        return card
