
import logging
from jass.agents.agent import Agent
from jass.game.game_observation import GameObservation
from jass.game.rule_schieber import RuleSchieber
from jass.agent_actions.actions import *


class AgentSimpleRule (Agent):
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

    def action_trump(self, obs: GameObservation) -> int:
        """
        Determine trump action for the given observation
        Args:
            obs: the match observation, it must be in a state for trump selection

        Returns:
            selected trump as encoded in jass.match.const or jass.match.const.PUSH
        """
        self._logger.info('Trump request')
        result = select_trump(obs.hand, obs.forehand)
        self._logger.info('Result: {}'.format(result))
        return result

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
            play_card = get_best_card_using_simple_rules_from_obs(obs, self._rule)
            self._logger.info('Played card: {}'.format(card_strings[play_card]))
            return play_card

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
