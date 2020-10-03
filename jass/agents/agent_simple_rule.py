
import logging
import numpy as np
from jass.agents.agent import Agent
from jass.game.game_observation import GameObservation
from jass.game.rule_schieber import RuleSchieber
from jass.game.const import *


class AgentSimpleRule (Agent):
    """
    Agent to act as a player in a match of jass.
    """
    def __init__(self):
        # log actions
        self._logger = logging.getLogger(__name__)
        # Use rule object to determine valid actions
        self._rule = RuleSchieber()

    def action_trump(self, obs: GameObservation) -> int:
        """
        Determine trump action for the given observation
        Args:
            obs: the match observation, it must be in a state for trump selection

        Returns:
            selected trump as encoded in jass.match.const or jass.match.const.PUSH
        """
        self._logger.info('Trump request')

        trump_card_sums = self.get_trump_card_sums(obs.hand)
        highest = max(trump_card_sums)

        if obs.forehand == -1:
            # if forehand is not yet set, we are the forehand player and can select trump or push
            if highest < 55:  # Threshold for pushing
                self._logger.info('Result: {}'.format(PUSH))
                return PUSH
        result = trump_card_sums.index(highest)
        self._logger.info('Result: {}'.format(result))
        return result

    def action_play_card(self, obs: GameObservation) -> int:
        """
        Determine the card to play.

        Args:
            obs: the match observation

        Returns:
            the card to play, int encoded as defined in jass.match.const
        """
        valid_cards = self._rule.get_valid_cards_from_obs(obs)
        trick_points = obs.trick_points

        # First turn and first player?
        if obs.nr_tricks == 0 and obs.nr_cards_in_trick == 0:
            if obs.trump == UNE_UFE:
                return self.get_lowest_card(valid_cards)
            elif obs.trump == OBE_ABE:
                return self.get_highest_card(valid_cards)
            else:
                return self.get_most_valuable_trump_card(valid_cards)
        pass

    def get_trump_card_sums(self, hand):
        card_indexes = [index for index, value in enumerate(hand) if value == 1]

        trump_card_sums = []
        for trump_card_values in card_values:
            iterator = np.nditer(trump_card_values, flags=["f_index"])
            trump_card_sum = sum([card_value for card_value in iterator if iterator.index in card_indexes])
            trump_card_sums.append(trump_card_sum)
        return trump_card_sums

    def get_lowest_card(self, valid_cards):
        return self.get_minmax_card(valid_cards, lambda x, y: x > y)

    def get_highest_card(self, valid_cards):
        return self.get_minmax_card(valid_cards, lambda x, y: x < y)

    def get_minmax_card(self, valid_cards, compare_index=None):
        edge_card = None
        edge_normalized_index = None
        for index, value in enumerate(valid_cards):
            normalized_index = index % 9  # 9 Cards per color in the array
            if value == 1 and (edge_card is None or compare_index(normalized_index,edge_normalized_index)):
                edge_card = index
                edge_normalized_index = normalized_index
        return edge_card
