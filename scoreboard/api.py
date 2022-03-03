

import urllib.request
import json
from actioncable.connection import Connection
from actioncable.subscription import Subscription
from scoreboard import logger

SERVER = "vb-scores.com"
HTTP = "https"
WS = "wss"

class Api:

    def __init__(self, api_key, log_level):
        self.api_key = api_key
        self.actioncable_logger = logger.getLogger('ActionCable Connection', int(log_level), api_key)
        self.score_subscription = None
        self.config_subscription = None
        self.connection = Connection(url=f'{WS}://{SERVER}/cable')
        self.connection.connect()
        self.logger = logger.getLogger('scoreboard', int(log_level), api_key)


    def subscribe_score_updates(self, callback):
        if self.score_subscription:
            self.score_subscription.remove()

        self.score_subscription = Subscription(self.connection, identifier={'channel': 'ScoreUpdatesChannel', 'api_key': self.api_key})
        self.score_subscription.on_receive(callback=callback)
        self.score_subscription.create()


    def subscribe_config_updates(self, callback):
        if self.config_subscription:
            self.config_subscription.remove()

        self.config_subscription = Subscription(self.connection, identifier={'channel': 'ScoreboardChannel', 'api_key': self.api_key})
        self.config_subscription.on_receive(callback=callback)
        self.config_subscription.create()


    def scoreboard(self):
        response = urllib.request.urlopen(f'{HTTP}://{SERVER}/apiv1/scoreboard.json?api_key='+self.api_key).read().decode()
        return json.loads(response)


    def scoreboard_software(self):
        response = urllib.request.urlopen(f'{HTTP}://{SERVER}/apiv1/scoreboard_software.json?api_key='+self.api_key).read().decode()
        return json.loads(response)


    def matches(self):
        response = urllib.request.urlopen(f'{HTTP}://{SERVER}/apiv1/matches.json?api_key='+self.api_key).read().decode()
        return json.loads(response)


    def start_game(self, match_id):
        response = urllib.request.urlopen(f'{HTTP}://{SERVER}/apiv1/matches/'+str(match_id)+'/start_game.json?api_key='+self.api_key).read().decode()
        return json.loads(response)


    def end_match(self, match_id):
        response = urllib.request.urlopen(f'{HTTP}://{SERVER}/apiv1/matches/'+str(match_id)+'/end_match.json?api_key='+self.api_key).read().decode()


    def team1_plus(self, game_id):
        if game_id:
            response = urllib.request.urlopen(f'{HTTP}://{SERVER}/apiv1/games/'+str(game_id)+'/team1_score_plus.json?api_key='+self.api_key).read().decode()



    def team1_minus(self, game_id):
        if game_id:
            response = urllib.request.urlopen(f'{HTTP}://{SERVER}/apiv1/games/'+str(game_id)+'/team1_score_minus.json?api_key='+self.api_key).read().decode()



    def team2_plus(self, game_id):
        if game_id:
            response = urllib.request.urlopen(f'{HTTP}://{SERVER}/apiv1/games/'+str(game_id)+'/team2_score_plus.json?api_key='+self.api_key).read().decode()



    def team2_minus(self, game_id):
        if game_id:
            response = urllib.request.urlopen(f'{HTTP}://{SERVER}/apiv1/games/'+str(game_id)+'/team2_score_minus.json?api_key='+self.api_key).read().decode()


    def end_game(self, game_id):
        response = urllib.request.urlopen(f'{HTTP}://{SERVER}/apiv1/games/'+str(game_id)+'/end_game.json?api_key='+self.api_key).read().decode()


    def get_serving_order(self, game_id):
        response = urllib.request.urlopen(f'{HTTP}://{SERVER}/apiv1/games/'+str(game_id)+'/get_serving_order.json?api_key='+self.api_key).read().decode()
        return json.loads(response)


    def set_serving_order(self, game_id, serve_order):
        response = urllib.request.urlopen(f'{HTTP}://{SERVER}/apiv1/games/'+str(game_id)+'/set_serving_order.json?api_key='+self.api_key+'&serving_order='+serve_order).read().decode()

