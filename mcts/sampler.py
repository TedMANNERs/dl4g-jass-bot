import numpy as np
from jass.game.const import *
from jass.game.game_observation import GameObservation


class Sampler:
    def get_random_sample(self, obs: GameObservation):
        other_player_cards = self._get_other_player_cards(obs)

        hands = np.zeros(shape=[4, 36])
        for player in range(MAX_PLAYER + 1):
            if player == obs.player:
                hands[player] = obs.hand
            else:
                hands[player], other_player_cards = self._get_random_hand(other_player_cards, player, obs)
        # print(other_player_cards)
        return hands

    def _get_other_player_cards(self, obs: GameObservation):
        # calculate which cards are still in the hands of players
        pre_hack_played_cards = np.concatenate([t for t in obs.tricks])
        # use ugly hack because tricks contain -1 for unplayed cards
        played_cards = pre_hack_played_cards[pre_hack_played_cards != -1]
        unplayed_cards = np.ones(36)
        for c in played_cards:
            unplayed_cards[c] = 0
        other_player_cards = unplayed_cards - obs.hand
        return other_player_cards

    def _get_random_hand(self, other_player_cards, player, obs: GameObservation):
        # use ugly hack because current_trick contains -1 for unplayed cards
        current_trick_cards = obs.current_trick[obs.current_trick != -1]
        nr_of_previous_players_with_less_cards = len(current_trick_cards)

        previous_player = [1, 2, 3, 0]

        # all players ahead of us receive the same number of cards
        nr_of_cards_to_receive = len(np.flatnonzero(obs.hand))

        # all previous players receive one less
        previous_p = obs.player
        for x in range(nr_of_previous_players_with_less_cards):
            previous_p = previous_player[previous_p]
            if previous_p == player:
                # 1 less card because they already played a card
                nr_of_cards_to_receive -= 1

        # Choose random cards from other_player_cards
        hand_to_receive = np.zeros(36)
        cards_to_receive = np.random.choice(np.flatnonzero(other_player_cards), nr_of_cards_to_receive, replace=False)
        for card in cards_to_receive:
            hand_to_receive[card] = 1
            # remove the cards from other_player_cards so the next player cannot receive the same cards
            other_player_cards[card] = 0

        return hand_to_receive, other_player_cards

    def get_hand_sizes(self, obs: GameObservation):
        hands = self.get_random_sample(obs)
        hand_sizes = []
        for hand in hands:
            cards = np.flatnonzero(hand)
            hand_sizes.append(len(cards))
        return hand_sizes
