import numpy as np
from jass.game.game_state import GameState
from jass.game.rule_schieber import RuleSchieber
from jass.game.game_sim import GameSim
from mcts.node import Node



class MonteCarloTreeSearch:
    def __init__(self, state:GameState, rule: RuleSchieber):
        self.root = Node(state)
        self._rule = rule
        self._exploration_weight = 1

    def get_best_node_from_simulation(self):
        leaf_node = self._select_next_node()
        leaf_node = self._expand_node(leaf_node)
        leaf_node = self._simulate(leaf_node)
        self._backpropagate(leaf_node)
        pass

    def _select_next_node(self):
        node = self.root
        while len(node.children) > 0 or not node.isExpanded:
            # TODO: Do we need to select unexplored nodes only?
            node = self.get_next_ucb1_child(node)
        return node

    def _expand_node(self, node: Node):
        if node.game_state.nr_played_cards < 36: # Is the game finished?
            child_node = self._play_single_turn(node)
            node.isExpanded = True
            return child_node
        else:
            return node

    def _simulate(self, leaf_node: Node):
        # nr_played_cards = len(leaf_node.get_path())
        current_node = leaf_node
        while current_node.game_state.nr_played_cards < 36: # Is the game finished?
            # play a card
            new_child_node = self._play_single_turn(current_node)
            current_node = new_child_node

        current_node.calculate_payoff()
        return current_node

    def _backpropagate(self, node: Node):
        while node.parent is not None:
            node.parent.accumulated_payoff += node.accumulated_payoff

    def _play_single_turn(self, node: Node):
        simulation = GameSim(self._rule)
        simulation.init_from_state(node.game_state)
        # Play a card from all players valid cards, since we play for them too
        possible_cards = self._get_valid_cards_from_all_hands(node.game_state)
        random_valid_card = np.random.choice(possible_cards, 1)  # TODO: Use rules here?
        simulation.action_play_card(random_valid_card)
        child_node = Node(simulation.state, node) # TODO: Is a new node always needed, what if we revisit it?
        node.children.append(child_node)
        return child_node

    def _get_valid_cards_from_all_hands(self, state: GameState):
        return self._rule.get_valid_cards(hand=np.sum(state.hands, axis=0),
                                          current_trick=state.current_trick,
                                          move_nr=state.nr_cards_in_trick,
                                          trump=state.trump)

    def get_next_ucb1_child(self, node: Node):
        max_ucb_child = node
        for child in node.children:
            exploration = self._exploration_weight * np.sqrt(np.log(self.root.visit_count) / node.visit_count)
            child.ucb = node.wins / node.visit_count + exploration
            if child.ucb > max_ucb_child.ucb:
                max_ucb_child = child
                max_ucb_child.visit_count += 1
        return max_ucb_child
