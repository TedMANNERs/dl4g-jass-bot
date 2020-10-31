import numpy as np
from jass.game.const import *
from jass.game.game_state import GameState
from jass.game.rule_schieber import GameRule
from jass.game.game_observation import GameObservation


def select_trump(hand, forehand):
    trump_card_sums = get_trump_card_sums(hand)
    highest = max(trump_card_sums)

    if forehand == -1:
        # if forehand is not yet set, we are the forehand player and can select trump or push
        if highest < 55:  # Threshold for pushing
            return PUSH
    return trump_card_sums.index(highest)

def get_trump_card_sums(hand):
    card_indexes = [index for index, value in enumerate(hand) if value == 1]

    trump_card_sums = []
    for trump_card_values in card_values:
        iterator = np.nditer(trump_card_values, flags=["f_index"])
        trump_card_sum = sum([card_value for card_value in iterator if iterator.index in card_indexes])
        trump_card_sums.append(trump_card_sum)
    return trump_card_sums


def get_highest_trump_card(valid_cards, trump):
    # all trumps in hand
    trump_cards = valid_cards * color_masks[trump, :]

    remaining_trump_cards = np.ones([36], np.int32)
    for index, value in enumerate(trump_cards):
        if value == 1:
            higher_trump_cards = trump_cards * higher_trump[index, :]
            remaining_trump_cards = higher_trump_cards * remaining_trump_cards
            if not remaining_trump_cards.any():  # all zeros, so no higher trump card
                return index
    print("Could not get highest trump card\nTrump Cards = {0}".format(trump_cards))
    raise ValueError("This should not happen!")


def get_lowest_trump_card(valid_cards, trump):
    # all trumps in hand
    trump_cards = valid_cards * color_masks[trump, :]

    remaining_trump_cards = np.ones([36], np.int32)
    for index, value in enumerate(trump_cards):
        if value == 1:
            lower_trump_cards = trump_cards * lower_trump[index, :]
            remaining_trump_cards = lower_trump_cards * remaining_trump_cards
            if sum(remaining_trump_cards) <= 1:  # all zeros except lowest trump
                return index
    print("Could not get lowest trump card\nTrump Cards = {0}".format(trump_cards))
    raise ValueError("This should not happen!")


def get_lowest_card(valid_cards):
    return get_minmax_card(valid_cards, lambda x, y: x > y)


def get_highest_card(valid_cards):
    return get_minmax_card(valid_cards, lambda x, y: x < y)


def get_minmax_card(valid_cards, compare_index=None):
    edge_card = None
    edge_normalized_index = None
    for index, value in enumerate(valid_cards):
        normalized_index = index % 9  # 9 Cards per color in the array
        if value == 1 and (edge_card is None or compare_index(normalized_index, edge_normalized_index)):
            edge_card = index
            edge_normalized_index = normalized_index
    return edge_card


def get_higher_non_trump_cards(non_trump_cards, current_trick):
    higher_non_trump_cards = np.zeros([36])
    highest_played_card = get_highest_card(current_trick)
    for index, value in enumerate(non_trump_cards):
        if value == 1 and index < highest_played_card:
            higher_non_trump_cards[index] = value

    return higher_non_trump_cards


def get_best_card_using_simple_rules_from_state(state: GameState, rule: GameRule):
    valid_cards = rule.get_valid_cards_from_state(state)
    return get_best_card_using_simple_rules(valid_cards, state.trump, state.current_trick, state.nr_cards_in_trick)


def get_best_card_using_simple_rules_from_obs(obs: GameObservation, rule: GameRule):
    valid_cards = rule.get_valid_cards_from_obs(obs)
    return get_best_card_using_simple_rules(valid_cards, obs.trump, obs.current_trick, obs.nr_cards_in_trick)


def get_best_card_using_simple_rules(valid_cards, trump, current_trick, nr_cards_in_trick):
    current_trick = resize_to_card_array(current_trick)
    current_trick_points = sum(current_trick * card_values[trump])

    # Simple rules for UNE_UFE and OBE_ABE
    if trump == UNE_UFE:
        return get_lowest_card(valid_cards)
    elif trump == OBE_ABE:
        return get_highest_card(valid_cards)

    # Now handling trumps
    valid_cards_contain_any_trump = (valid_cards * color_masks[trump]).any()
    # Am I the first player?
    if nr_cards_in_trick == 0 and valid_cards_contain_any_trump:
        return get_highest_trump_card(valid_cards, trump)

    # Start off with the worst cards if not the first player in a trick
    play_card = get_lowest_card(valid_cards)

    trick_trump_cards = current_trick * color_masks[trump]
    non_trump_cards = valid_cards * (np.ones([36]) - color_masks[trump])

    if not trick_trump_cards.any():
        higher_non_trump_cards = get_higher_non_trump_cards(non_trump_cards, current_trick)
        if higher_non_trump_cards.any():
            play_card = get_highest_card(valid_cards)
            if current_trick_points > 8 and valid_cards_contain_any_trump:
                play_card = get_lowest_trump_card(valid_cards, trump)
    elif current_trick_points > 10 and valid_cards_contain_any_trump:
        play_card = get_lowest_trump_card(valid_cards, trump)
    return play_card


def resize_to_card_array(card_indexes):
    cards = np.zeros([36])
    for card_index in card_indexes:
        cards[card_index] = 1
    return cards
