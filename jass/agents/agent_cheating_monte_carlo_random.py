import time
import logging
import numpy as np
from jass.agents.agent import CheatingAgent
from jass.game.game_state import GameState
from jass.game.rule_schieber import RuleSchieber
from jass.game.const import *
from mcts.mcts import MonteCarloTreeSearch
from jass.agent_actions.actions import *
from mcts.turn_action import RandomTurnAction


class AgentCheatingMonteCarloRandom (CheatingAgent):
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
        search_tree = MonteCarloTreeSearch(state, self._rule, RandomTurnAction())
        node = search_tree.get_best_node_from_simulation()
        start_time = time.time()
        while time.time() - start_time <= self.simulation_time:
            node = search_tree.get_best_node_from_simulation()

        card = node.card
        self._logger.info('Played card: {}'.format(card_strings[card]))
        return card
