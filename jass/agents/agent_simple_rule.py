
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
        valid_cards = self._rule.get_valid_cards_from_obs(obs)
        current_trick = self.resize_to_card_array(obs.current_trick)

        try:
            current_trick_points = sum(current_trick * card_values[obs.trump])

            # Simple rules for UNE_UFE and OBE_ABE
            if obs.trump == UNE_UFE:
                return get_lowest_card(valid_cards)
            elif obs.trump == OBE_ABE:
                return get_highest_card(valid_cards)

            # Now handling trumps
            valid_cards_contain_any_trump = (valid_cards * color_masks[obs.trump]).any()
            # Am I the first player?
            if obs.nr_cards_in_trick == 0 and valid_cards_contain_any_trump:
                return get_highest_trump_card(valid_cards, obs.trump)

            # Start off with the worst cards if not the first player in a trick
            play_card = get_lowest_card(valid_cards)

            trick_trump_cards = current_trick * color_masks[obs.trump]
            non_trump_cards = valid_cards * (np.ones([36]) - color_masks[obs.trump])

            if not trick_trump_cards.any():
                higher_non_trump_cards = get_higher_non_trump_cards(non_trump_cards, current_trick)
                if higher_non_trump_cards.any():
                    play_card = get_highest_card(valid_cards)
                    if current_trick_points > 8 and valid_cards_contain_any_trump:
                        play_card = get_lowest_trump_card(valid_cards, obs.trump)
            elif current_trick_points > 10 and valid_cards_contain_any_trump:
                play_card = get_lowest_trump_card(valid_cards, obs.trump)

            self._logger.info('Played card: {}'.format(card_strings[play_card]))
            return play_card

        except Exception as e:

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

    def resize_to_card_array(self, card_indexes):
        cards = np.zeros([36])
        for card_index in card_indexes:
            cards[card_index] = 1
        return cards
