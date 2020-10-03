import unittest

from jass.agents.agent_simple_rule import AgentSimpleRule
from jass.game.game_util import *
from jass.game.const import *


class JassAgentTestCase(unittest.TestCase):

    def test_get_trump_card_sums(self):
        agent = AgentSimpleRule()
        hand = deal_random_hand()[0]
        print(hand)
        card_indexes = [index for index, value in enumerate(hand) if value == 1]
        print([card_strings[index] for index in card_indexes])
        trump_card_sums = agent.get_trump_card_sums(hand)
        print(trump_card_sums)


if __name__ == '__main__':
    unittest.main()