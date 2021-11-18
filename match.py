
import json
from collections import deque


class Match:
    def __init__(self):
        self.info = {}
        self.info['mode'] = 'score'
        self.team1('Team 1')
        self.team2('Team 2')
        self.reset()


    def reset(self):
        self.game_id = None
        self.set(0)
        self.team1_left = True
        self.team1_score(0)
        self.team2_score(0)
        self.serving_order([1,3])
        self.server(self.serve_order[0])


    def set(self, set=None):
        if set == None:
            return self.info['set']
        self.info['set'] = set


    def team1(self, name=None):
        if name == None:
            return self.info['team1']
        self.info['team1'] = name.strip()
        players = self.info['team1'].split('/')
        if len(players) > 0:
            self.info['player1'] = players[0]
        else:
            self.info['player1'] = ""
        if len(players) > 1:
            self.info['player2'] = players[1]
        else:
            self.info['player2'] = ""


    def team2(self, name=None):
        if name == None:
            return self.info['team2']
        self.info['team2'] = name.strip()
        players = self.info['team2'].split('/')
        if len(players) > 0:
            self.info['player3'] = players[0]
        else:
            self.info['player3'] = ""
        if len(players) > 1:
            self.info['player4'] = players[1]
        else:
            self.info['player4'] = ""


    def player1(self):
        return self.info['player1']


    def player2(self):
        return self.info['player2']


    def player3(self):
        return self.info['player3']


    def player4(self):
        return self.info['player4']


    def team1_score(self, score=None):
        if score == None:
            return self.info['team1_score']
        self.info['team1_score'] = score


    def team2_score(self, score=None):
        if score == None:
            return self.info['team2_score']
        self.info['team2_score'] = score


    def server(self, server=None):
        if server == None:
            return self.info['server']
        self.info['server'] = server


    def team1_add_point(self):
        self.info['team1_score'] += 1
        if self.info['server'] in [3,4]:
            self.serve_order.rotate()
            self.info['server'] = self.serve_order[0]


    def team2_add_point(self):
        self.info['team2_score'] += 1
        if self.info['server'] in [1,2]:
            self.serve_order.rotate()
            self.info['server'] = self.serve_order[0]


    def team1_subtract_point(self):
        self.info['team1_score'] = max(0, self.info['team1_score'] - 1)


    def team2_subtract_point(self):
        self.info['team2_score'] = max(0, self.info['team2_score'] - 1)


    def serving_order(self, order):
        self.serve_order = deque(order)


    def switch_sides(self):
        self.team1_left = not self.team1_left


    def left_score(self, score=None):
        if self.team1_left:
            return self.team1_score(score)
        else:
            return self.team2_score(score)


    def right_score(self, score=None):
        if self.team1_left:
            return self.team2_score(score)
        else:
            return self.team1_score(score)


    def left_server(self):
        if self.team1_left:
            return self.server() in [1,2]
        else:
            return self.server() in [3,4]


    def right_server(self):
        if self.team1_left:
            return self.server() in [3,4]
        else:
            return self.server() in [1,2]


    def left_add_point(self):
        if self.team1_left:
            self.team1_add_point()
        else:
            self.team2_add_point()


    def right_add_point(self):
        if self.team1_left:
            self.team2_add_point()
        else:
            self.team1_add_point()


    def left_subtract_point(self):
        if self.team1_left:
            self.team1_subtract_point()
        else:
            self.team2_subtract_point()


    def right_subtract_point(self):
        if self.team1_left:
            self.team2_subtract_point()
        else:
            self.team1_subtract_point()

