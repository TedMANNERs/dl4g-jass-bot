# HSLU
#
# Created by Thomas Koller on 7/28/2020
#
import logging
import numpy as np
from jass.agents.agent import CheatingAgent
from jass.game.const import PUSH, MAX_TRUMP, card_strings
from jass.game.game_state import GameState
from jass.game.rule_schieber import RuleSchieber


class AgentCheatingRandomSchieber (CheatingAgent):
    """
    Randomly select actions for the match of jass (Schieber)
    """
    def __init__(self):
        # log actions
        self._logger = logging.getLogger(__name__)
        # self._logger.setLevel(logging.INFO)
        # Use rule object to determine valid actions
        self._rule = RuleSchieber()
        # init random number generator
        self._rng = np.random.default_rng()

    def action_trump(self, state: GameState) -> int:
        """
        Select trump randomly. Pushing is selected with probability 0.5 if possible.
        Args:
            state: the current match
        Returns:
            trump action
        """
        self._logger.info('Trump request')
        if state.forehand == -1:
            # if forehand is not yet set, we are the forehand player and can select trump or push
            if self._rng.choice([True, False]):
                self._logger.info('Result: {}'.format(PUSH))
                return PUSH
        # if not push or forehand, select a trump
        result = int(self._rng.integers(low=0, high=MAX_TRUMP, endpoint=True))
        self._logger.info('Result: {}'.format(result))
        return result

    def action_play_card(self, state: GameState) -> int:
        """
        Select randomly a card from the valid cards
        Args:
            state: The state of the jass match for the current player
        Returns:
            card to play
        """
        self._logger.info('Card request')
        # cards are one hot encoded
        valid_cards = self._rule.get_valid_cards_from_state(state)
        # convert to list and draw a value
        card = self._rng.choice(np.flatnonzero(valid_cards))
        self._logger.info('Played card: {}'.format(card_strings[card]))
        return card

