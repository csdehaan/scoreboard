
import json
from collections import deque


class Match:
    def __init__(self):
        self.info = {}
        self.info['mode'] = 'score'
        self.info['t1_players'] = []
        self.info['t2_players'] = []
        self.team1('Team 1')
        self.team2('Team 2')
        self.reset()


    def reset(self):
        self.game_id = None
        self.set(0)
        self.team1_score(0)
        self.team2_score(0)
        self.server(self.serve_order[0])


    def set(self, set=None):
        if set == None:
            return self.info['set']
        self.info['set'] = set


    def team1(self, name=None):
        if name == None:
            return self.info['team1']
        self.info['team1'] = name.strip()
        self.info['t1_players'] = self.info['team1'].split('/')
        if len(self.info['t1_players']) == len(self.info['t2_players']):
            self.serving_order(sum(list(map(lambda x: [x,x+10], range(11,11+len(self.info['t1_players'])))), []))
        else:
            self.serving_order([0])


    def team2(self, name=None):
        if name == None:
            return self.info['team2']
        self.info['team2'] = name.strip()
        self.info['t2_players'] = self.info['team2'].split('/')
        if len(self.info['t1_players']) == len(self.info['t2_players']):
            self.serving_order(sum(list(map(lambda x: [x,x+10], range(11,11+len(self.info['t2_players'])))), []))
        else:
            self.serving_order([0])


    def player(self, team, player):
        try:
            if team == 1:
                return self.info['t1_players'][player-1]
            if team == 2:
                return self.info['t2_players'][player-1]
        except:
            pass
        return None


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
        if self.info['server'] in range(21,30):
            self.serve_order.rotate()
            self.info['server'] = self.serve_order[0]


    def team2_add_point(self):
        self.info['team2_score'] += 1
        if self.info['server'] in range(11,20):
            self.serve_order.rotate()
            self.info['server'] = self.serve_order[0]


    def team1_subtract_point(self):
        self.info['team1_score'] = max(0, self.info['team1_score'] - 1)


    def team2_subtract_point(self):
        self.info['team2_score'] = max(0, self.info['team2_score'] - 1)


    def serving_order(self, order):
        self.serve_order = deque(order)
