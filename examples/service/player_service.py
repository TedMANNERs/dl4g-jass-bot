# HSLU
#
# Created by Thomas Koller on 7/30/2020
#
"""
Example how to use flask to create a service for one or more players
"""
import logging
import os

from jass.agents.agent_monte_carlo import AgentMonteCarlo
from jass.agents.agent_simple_rule import AgentSimpleRule
from jass.service.player_service_app import PlayerServiceApp
from jass.agents.agent_random_schieber import AgentRandomSchieber


def create_app():
    """
    This is the factory method for flask. It is automatically detected when flask is run, but we must tell flask
    what python file to use:

        export FLASK_APP=player_service.py
        export FLASK_ENV=development
        flask run --host=0.0.0.0 --port=8888
    """
    logging.basicConfig(level=logging.DEBUG)

    # create and configure the app
    app = PlayerServiceApp('player_service')

    # you could use a configuration file to load additional variables
    # app.config.from_pyfile('my_player_service.cfg', silent=False)

    # add some players
    app.add_player('migrosoft_random', AgentRandomSchieber())
    app.add_player('migrosoft_simple_rule', AgentSimpleRule())
    app.add_player('migrosoft_ismcts', AgentMonteCarlo(1.0))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

