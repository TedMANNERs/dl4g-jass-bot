from abc import ABC

import numpy as np

from jass.agent_actions.actions import get_best_card_using_simple_rules_from_obs
from jass.game.game_rule import GameRule
from jass.game.game_sim import GameSim
from jass.game.game_observation import GameObservation


class TurnAction(ABC):
    def play_single_turn(self, hands, obs: GameObservation, rule: GameRule) -> GameObservation:
        raise NotImplementedError


class RandomTurnAction(TurnAction):
    def play_single_turn(self, hands, obs: GameObservation, rule: GameRule) -> GameObservation:
        simulation = GameSim(rule)
        simulation.init_from_cards(hands, obs.dealer)

        valid_cards = rule.get_valid_cards_from_obs(obs)
        random_valid_card = np.random.choice(np.flatnonzero(valid_cards))
        simulation.action_play_card(random_valid_card)
        return simulation.state


class HeuristicTurnAction(TurnAction):
    def play_single_turn(self, hands, obs: GameObservation, rule: GameRule) -> GameObservation:
        simulation = GameSim(rule)
        simulation.init_from_cards(hands, obs.dealer)
        best_card = get_best_card_using_simple_rules_from_obs(obs, rule)
        simulation.action_play_card(best_card)
        return simulation.state
