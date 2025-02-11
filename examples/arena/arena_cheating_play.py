import logging
from jass.arena.arena_cheating import ArenaCheating
from jass.agents.agent_cheating_monte_carlo import AgentCheatingMonteCarlo
from jass.agents.agent_cheating_monte_carlo_random import AgentCheatingMonteCarloRandom
from jass.agents.agent_cheating_random_schieber import AgentCheatingRandomSchieber


def main():
    # Set the global logging level (Set to debug or info to see more messages)
    logging.basicConfig(level=logging.WARNING)

    # setup the arena
    arena = ArenaCheating(nr_games_to_play=3, save_filename='arena_games')
    north = AgentCheatingMonteCarlo(1)  # Team 0
    south = AgentCheatingRandomSchieber()  # Team 0
    east = AgentCheatingMonteCarloRandom(1)  # Team 1
    west = AgentCheatingRandomSchieber()  # Team 1

    arena.set_players(north, east, south, west)
    print('Playing {} games'.format(arena.nr_games_to_play))
    arena.play_all_games()
    print('Average Points Team 0: {:.2f})'.format(arena.points_team_0.mean()))
    print('Average Points Team 1: {:.2f})'.format(arena.points_team_1.mean()))


if __name__ == '__main__':
    main()
