import time
import logging
import numpy as np
from jass.agents.agent import Agent
from jass.game.game_observation import GameObservation
from jass.game.rule_schieber import RuleSchieber
from jass.game.const import *
from mcts.mcts import MonteCarloTreeSearch
from jass.agent_actions.actions import *
from mcts.turn_action import HeuristicTurnAction


class AgentMonteCarlo (Agent):
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
        self.other_player_cards = []

    def action_trump(self, obs: GameObservation) -> int:
        self._logger.info('Trump request')
        result = select_trump(obs.hand, obs.forehand)
        self._logger.info('Result: {}'.format(result))
        return result

    def action_play_card(self, obs: GameObservation) -> int:
        search_tree = MonteCarloTreeSearch(obs, self._rule, HeuristicTurnAction())
        node = search_tree.get_best_node_from_simulation()
        start_time = time.time()
        while time.time() - start_time <= self.simulation_time:
            node = search_tree.get_best_node_from_simulation()

        card = node.card
        self._logger.info('Played card: {}'.format(card_strings[card]))
        return card
