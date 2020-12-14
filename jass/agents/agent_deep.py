
import logging
import pandas as pd
from tensorflow import keras
from jass.agents.agent import Agent
from jass.game.game_observation import GameObservation
from jass.game.rule_schieber import RuleSchieber
from jass.agent_actions.actions import *


class AgentDeep (Agent):
    """
    Agent to act as a player in a match of jass.
    """
    def __init__(self):
        # log actions
        self._logger = logging.getLogger(__name__)
        # Use rule object to determine valid actions
        self._rule = RuleSchieber()
        # init random number generator
        self._rng = np.random.default_rng()
        self.trump_model = keras.models.load_model('../../models/trump0631')
        self.cards_model = keras.models.load_model('../../models/CardsModel05865')

    def action_trump(self, obs: GameObservation) -> int:
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
        # result = pd.DataFrame(data=prediction,
        #                      columns=["DIAMONDS", "HEARTS", "SPADES", "CLUBS", "OBE_ABE", "UNE_UFE", "PUSH"])
        # print(result)
        max_index = np.argmax(prediction)

        if max_index == PUSH_ALT:
            max_index = PUSH
            if obs.forehand != -1:
                # we are the forehand player and must select trump
                max_index = np.argmax(prediction[:-1])  # everything except last value (PUSH)

        self._logger.info('Result: {}'.format(max_index))
        return max_index

    # TODO: color_masks does not work for UNE_UFE and OBE_ABE (separate logic?)
    def action_play_card(self, obs: GameObservation) -> int:
        """
        Determine the card to play.

        Args:
            obs: the match observation

        Returns:
            the card to play, int encoded as defined in jass.match.const
        """
        try:
            valid_cards = self._rule.get_valid_cards_from_obs(obs)
            model_input = np.append(valid_cards, [obs.trump])
            model_input = np.array([model_input])
            prediction = self.cards_model.predict(model_input)
            prediction = prediction * valid_cards
            best_card = int(np.argmax(prediction))

            self._logger.info('Played card: {}'.format(card_strings[best_card]))
            return best_card

        except Exception as e:
            valid_cards = self._rule.get_valid_cards_from_obs(obs)
            self._logger.error("\n"
                               "Hand          = {0}\n"
                               "Valid Cards   = {1}\n"
                               "Trump         = {2}\n"
                               "Current Trick = {3}"
                               .format(obs.hand, valid_cards, obs.trump, obs.current_trick))
            self._logger.error("Rule failed. Continuing with random card.", e)
            card = self._rng.choice(np.flatnonzero(valid_cards))
            self._logger.info('Played card: {}'.format(card_strings[card]))
            return card
