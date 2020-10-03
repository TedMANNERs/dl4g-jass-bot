import unittest

from jass.agents.agent_simple_rule import AgentSimpleRule
from jass.game.game_observation import GameObservation
from jass.game.game_util import *
from jass.game.const import *
import numpy as np


class JassAgentTestCase(unittest.TestCase):

    def test_action_play_card(self):
        agent = AgentSimpleRule()
        obs = GameObservation()

        obs.hand = deal_random_hand()[0]
        print("Hand = {0}".format(obs.hand))
        obs.current_trick = [DA]
        obs.nr_cards_in_trick = len(obs.current_trick)
        print("Current Trick = {0}".format(obs.current_trick))
        obs.trump = DIAMONDS
        print("Trump = {0}".format(obs.trump))
        valid_cards = agent._rule.get_valid_cards_from_obs(obs)
        print("Valid Cards = {0}".format(valid_cards))

        card = agent.action_play_card(obs)
        print("Played Card = {0}".format(card))

    def test_get_trump_card_sums(self):
        agent = AgentSimpleRule()
        hand = deal_random_hand()[0]
        print(hand)
        card_indexes = [index for index, value in enumerate(hand) if value == 1]
        print([card_strings[index] for index in card_indexes])
        trump_card_sums = agent.get_trump_card_sums(hand)
        print(trump_card_sums)

    def test_get_lowest_card(self):
        agent = AgentSimpleRule()
        hand = deal_random_hand()[0]
        #hand = [1,0,0,0,1,0,0,0,0, 1,0,0,0,0,1,0,1,0, 0,0,0,0,1,0,0,0,0, 1,0,1,0,0,0,0,0,0]
        for arr in np.array_split(hand, 4):
            print(arr)
        lowest = agent.get_lowest_card(hand)
        print(lowest)

    def test_get_highest_card(self):
        agent = AgentSimpleRule()
        hand = deal_random_hand()[0]
        for arr in np.array_split(hand, 4):
            print(arr)
        highest = agent.get_highest_card(hand)
        print(highest)

    def test_get_highest_trump_card(self):
        agent = AgentSimpleRule()
        hand = deal_random_hand()[0]
        #hand = [1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        for arr in np.array_split(hand, 4):
            print(arr)
        trump = agent.get_highest_trump_card(hand, DIAMONDS)
        print(trump)

    def test_get_lowest_trump_card(self):
        agent = AgentSimpleRule()
        hand = deal_random_hand()[0]
        hand = [1,0,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        for arr in np.array_split(hand, 4):
            print(arr)
        trump = agent.get_lowest_trump_card(hand, DIAMONDS)
        print(trump)


if __name__ == '__main__':
    unittest.main()
