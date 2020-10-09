
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
                return self.get_lowest_card(valid_cards)
            elif obs.trump == OBE_ABE:
                return self.get_highest_card(valid_cards)

            # Now handling trumps
            # Am I the first player?
            if obs.nr_cards_in_trick == 0:
                return self.get_highest_trump_card(valid_cards, obs.trump)

            # Start off with the worst cards if not the first player in a trick
            play_card = self.get_lowest_card(valid_cards)

            trick_trump_cards = current_trick * color_masks[obs.trump]
            non_trump_cards = valid_cards * (np.ones([36]) - color_masks[obs.trump])
            valid_cards_contain_any_trump = (valid_cards * color_masks[obs.trump]).any()

            if not trick_trump_cards.any():
                higher_non_trump_cards = self.get_higher_non_trump_cards(non_trump_cards, current_trick)
                if higher_non_trump_cards.any():
                    play_card = self.get_highest_card(valid_cards)
                    if current_trick_points > 8 and valid_cards_contain_any_trump:
                        play_card = self.get_lowest_trump_card(valid_cards, obs.trump)
            elif current_trick_points > 10 and valid_cards_contain_any_trump:
                play_card = self.get_lowest_trump_card(valid_cards, obs.trump)

            self._logger.info('Played card: {}'.format(card_strings[play_card]))
            return play_card

        except Exception as e:

            self._logger.error("Hand          = {0}\n"
                               "Current Trick = {1}\n"
                               "Trump         = {2}\n"
                               "Valid Cards   = {3}"
                               .format(obs.hand, obs.current_trick, obs.trump, valid_cards))
            self._logger.error("Rule failed. Continuing with random card.", e)
            card = self._rng.choice(np.flatnonzero(valid_cards))
            self._logger.info('Played card: {}'.format(card_strings[card]))
            return card

    def resize_to_card_array(self, card_indexes):
        cards = np.zeros([36])
        for card_index in card_indexes:
            cards[card_index] = 1
        return cards

    def get_trump_card_sums(self, hand):
        card_indexes = [index for index, value in enumerate(hand) if value == 1]

        trump_card_sums = []
        for trump_card_values in card_values:
            iterator = np.nditer(trump_card_values, flags=["f_index"])
            trump_card_sum = sum([card_value for card_value in iterator if iterator.index in card_indexes])
            trump_card_sums.append(trump_card_sum)
        return trump_card_sums

    def get_highest_trump_card(self, valid_cards, trump):
        # all trumps in hand
        trump_cards = valid_cards * color_masks[trump, :]
        print(trump_cards)

        remaining_trump_cards = np.ones([36], np.int32)
        for index, value in enumerate(trump_cards):
            if value == 1:
                higher_trump_cards = trump_cards * higher_trump[index, :]
                remaining_trump_cards = higher_trump_cards * remaining_trump_cards
                if not remaining_trump_cards.any():  # all zeros, so no higher trump card
                    return index
        raise ValueError("This should not happen!")

    def get_lowest_trump_card(self, valid_cards, trump):
        # all trumps in hand
        trump_cards = valid_cards * color_masks[trump, :]
        print(trump_cards)

        remaining_trump_cards = np.ones([36], np.int32)
        for index, value in enumerate(trump_cards):
            if value == 1:
                lower_trump_cards = trump_cards * lower_trump[index, :]
                remaining_trump_cards = lower_trump_cards * remaining_trump_cards
                if sum(remaining_trump_cards) <= 1:  # all zeros except lowest trump
                    return index
        raise ValueError("This should not happen!")

    def get_lowest_card(self, valid_cards):
        return self.get_minmax_card(valid_cards, lambda x, y: x > y)

    def get_highest_card(self, valid_cards):
        return self.get_minmax_card(valid_cards, lambda x, y: x < y)

    def get_minmax_card(self, valid_cards, compare_index=None):
        edge_card = None
        edge_normalized_index = None
        for index, value in enumerate(valid_cards):
            normalized_index = index % 9  # 9 Cards per color in the array
            if value == 1 and (edge_card is None or compare_index(normalized_index, edge_normalized_index)):
                edge_card = index
                edge_normalized_index = normalized_index
        return edge_card

    def get_higher_non_trump_cards(self, non_trump_cards, current_trick):
        higher_non_trump_cards = np.zeros([36])
        highest_played_card = self.get_highest_card(current_trick)
        for index, value in enumerate(non_trump_cards):
            if value == 1 and index < highest_played_card:
                higher_non_trump_cards[index] = value

        return higher_non_trump_cards
