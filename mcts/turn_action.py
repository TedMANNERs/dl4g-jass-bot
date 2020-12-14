from abc import ABC

import numpy as np
import logging
from jass.agent_actions.actions import get_best_card_using_simple_rules_from_state
from jass.game.game_rule import GameRule
from jass.game.game_sim import GameSim
from jass.game.game_state import GameState
from jass.game.const import *


class TurnAction(ABC):
    def play_single_turn(self, game_state: GameState, rule: GameRule) -> GameState:
        raise NotImplementedError


class RandomTurnAction(TurnAction):
    def play_single_turn(self, game_state: GameState, rule: GameRule) -> GameState:
        simulation = GameSim(rule)
        simulation.init_from_state(game_state)

        valid_cards = rule.get_valid_cards_from_state(game_state)
        random_valid_card = np.random.choice(np.flatnonzero(valid_cards))
        simulation.action_play_card(random_valid_card)
        return simulation.state


class HeuristicTurnAction(TurnAction):
    def play_single_turn(self, game_state: GameState, rule: GameRule) -> GameState:
        simulation = GameSim(rule)
        simulation.init_from_state(game_state)

        best_card = get_best_card_using_simple_rules_from_state(game_state, rule)
        simulation.action_play_card(best_card)
        return simulation.state


class DeepTurnAction(TurnAction):
    def __init__(self, keras_model):
        self.keras_model = keras_model
        self._logger = logging.getLogger(__name__)

    def play_single_turn(self, game_state: GameState, rule: GameRule) -> GameState:
        simulation = GameSim(rule)
        simulation.init_from_state(game_state)

        valid_cards = rule.get_valid_cards_from_state(game_state)
        model_input = np.append(valid_cards, [game_state.trump])
        model_input = np.array([model_input])
        prediction = self.keras_model.predict(model_input)
        prediction = prediction * valid_cards
        best_card = int(np.argmax(prediction))

        self._logger.info('Predicted card = {}'.format(card_strings[best_card]))
        simulation.action_play_card(best_card)
        return simulation.state
