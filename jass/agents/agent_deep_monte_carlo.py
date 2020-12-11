import time
import logging
import numpy as np
import tensorflow as tf
from tensorflow import keras
from jass.agents.agent import Agent
from jass.game.game_observation import GameObservation
from jass.game.rule_schieber import RuleSchieber
from jass.game.const import *
from mcts.mcts import MonteCarloTreeSearch
from jass.agent_actions.actions import *
from mcts.turn_action import HeuristicTurnAction

class AgentDeepMonteCarlo(Agent):
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

        physical_devices = tf.config.list_physical_devices('GPU')
        tf.config.experimental.set_memory_growth(physical_devices[0], True)
        self.trump_model = keras.models.load_model('../../models/trump')

    def action_trump(self, obs: GameObservation) -> int:
        self._logger.info('Trump request')

        trump_points = get_trump_card_sums(obs.hand)
        # predict returns array with probabilities for each trump choice + PUSH (7 Values)
        prediction = self.trump_model.predict(np.array([trump_points]))
        prediction = prediction[0]
        max_index = np.argmax(prediction)

        if max_index == PUSH_ALT:
            max_index = PUSH
            if obs.forehand != -1:
                # we are the forehand player and must select trump
                max_index = np.argmax(prediction[:-1])  # everything except last value (PUSH)

        self._logger.info('Result: {}'.format(max_index))
        return max_index

    def action_play_card(self, obs: GameObservation) -> int:
        search_tree = MonteCarloTreeSearch(obs, self._rule, HeuristicTurnAction())
        node = search_tree.get_best_node_from_simulation()
        start_time = time.time()
        while time.time() - start_time <= self.simulation_time:
            node = search_tree.get_best_node_from_simulation()

        card = node.card
        self._logger.info('Played card: {}'.format(card_strings[card]))
        return card
