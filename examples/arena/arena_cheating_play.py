import logging
from jass.arena.arena_cheating import ArenaCheating
from jass.agents.agent_cheating_monte_carlo import AgentCheatingMonteCarlo


def main():
    # Set the global logging level (Set to debug or info to see more messages)
    logging.basicConfig(level=logging.WARNING)

    # setup the arena
    arena = ArenaCheating(nr_games_to_play=1000, save_filename='arena_games')
    player = AgentCheatingMonteCarlo(2)
    my_player = AgentCheatingMonteCarlo(2)

    arena.set_players(my_player, player, my_player, player)
    print('Playing {} games'.format(arena.nr_games_to_play))
    arena.play_all_games()
    print('Average Points Team 0: {:.2f})'.format(arena.points_team_0.mean()))
    print('Average Points Team 1: {:.2f})'.format(arena.points_team_1.mean()))


if __name__ == '__main__':
    main()
