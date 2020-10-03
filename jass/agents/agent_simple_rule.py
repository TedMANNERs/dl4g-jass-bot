
import logging
from jass.game.game_observation import GameObservation
from jass.game.const import *


class AgentSimpleRule:
    """
    Agent to act as a player in a match of jass.
    """
    def __init__(self):
        # log actions
        self._logger = logging.getLogger(__name__)

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
        raise NotImplementedError

    def get_trump_card_sums(self, hand):
        card_indexes = [index for index, value in enumerate(hand) if value == 1]

        trump_card_sums = []
        for trump_card_values in card_values:
            iterator = np.nditer(trump_card_values, flags=["f_index"])
            trump_card_sum = sum([card_value for card_value in iterator if iterator.index in card_indexes])
            trump_card_sums.append(trump_card_sum)
        return trump_card_sums
