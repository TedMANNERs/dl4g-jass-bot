import unittest

from jass.agents.agent_simple_rule import AgentSimpleRule
from jass.game.game_util import *
from jass.game.const import *
import numpy as np


class JassAgentTestCase(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()
