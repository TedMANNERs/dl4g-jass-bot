import time
import logging
import numpy as np
import tensorflow as tf
import pandas as pd
from tensorflow import keras
from jass.agents.agent import Agent
from jass.game.game_observation import GameObservation
from jass.game.rule_schieber import RuleSchieber
from jass.game.const import *
from mcts.mcts import MonteCarloTreeSearch
from jass.agent_actions.actions import *
from mcts.turn_action import HeuristicTurnAction

class AgentDeepTrumpMonteCarlo(Agent):
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

        #physical_devices = tf.config.list_physical_devices('GPU')
        #tf.config.experimental.set_memory_growth(physical_devices[0], True)
        self.trump_model = keras.models.load_model('../../models/trump0631')

    def action_trump(self, obs: GameObservation) -> int:
        self._logger.info('Trump request')

        # predict returns array with probabilities for each trump choice + PUSH (7 Values)
        hand = np.array([obs.hand])
        cards = [
            # Diamonds
            'DA', 'DK', 'DQ', 'DJ', 'D10', 'D9', 'D8', 'D7', 'D6',
            # Hearts
            'HA', 'HK', 'HQ', 'HJ', 'H10', 'H9', 'H8', 'H7', 'H6',
            # Spades
            'SA', 'SK', 'SQ', 'SJ', 'S10', 'S9', 'S8', 'S7', 'S6',
            # Clubs
            'CA', 'CK', 'CQ', 'CJ', 'C10', 'C9', 'C8', 'C7', 'C6'
        ]
        hand = pd.DataFrame(data=hand, columns=cards)
        for color in 'DHSC':
            # Jack and nine combination
            new_col = '{}_J9'.format(color)
            hand[new_col] = hand['{}J'.format(color)] & hand['{}9'.format(color)]

            # Ace King and Queen
            new_col = '{}_AKQ'.format(color)
            hand[new_col] = hand['{}A'.format(color)] & hand['{}K'.format(color)] & hand['{}Q'.format(color)]

            # Ace and King
            new_col = '{}_AK'.format(color)
            hand[new_col] = hand['{}A'.format(color)] & hand['{}K'.format(color)]

            # Ace Jack and Nine
            new_col = '{}_AJ9'.format(color)
            hand[new_col] = hand['{}A'.format(color)] & hand['{}J'.format(color)] & hand['{}9'.format(color)]

            # Acem Jack, King, Queen
            new_col = '{}_AJKQ'.format(color)
            hand[new_col] = hand['{}A'.format(color)] & hand['{}J'.format(color)] & hand['{}K'.format(color)] & hand[
                '{}Q'.format(color)]

            # Ace, 9, King, Queen
            new_col = '{}_A9KQ'.format(color)
            hand[new_col] = hand['{}A'.format(color)] & hand['{}9'.format(color)] & hand['{}K'.format(color)] & hand[
                '{}Q'.format(color)]

        input_hand = np.array([hand.iloc[0].values])
        prediction = self.trump_model.predict(input_hand)
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
            print('Do MCTS')
            node = search_tree.get_best_node_from_simulation()

        card = node.card
        self._logger.info('Played card: {}'.format(card_strings[card]))
        return card
