
from collections import deque


class Match:
    def __init__(self):
        self.info = {}
        self.info['t1_players'] = []
        self.info['t2_players'] = []
        self.info['referee'] = ''
        self.team1('Team 1')
        self.team2('Team 2')
        self.reset()


    def reset(self):
        self.game_id = None
        self.set(0)
        self.team1_sets(0)
        self.team2_sets(0)
        self.team1_score(0)
        self.team2_score(0)
        self.server(self.serve_order[0])
        self.side_switch(False)


    def from_json(self, js):
        self.team1(js['team1_name'])
        self.team2(js['team2_name'])
        self.set(len(js['games']))
        self.team1_sets(js['games_team1'])
        self.team2_sets(js['games_team2'])
        self.team1_score(js['games'][-1]['team1_score'])
        self.team2_score(js['games'][-1]['team2_score'])
        self.info['server'] = js['games'][-1]['server_number']
        self.side_switch(js['games'][-1]['switch_sides?'])
        self.game_id = js['games'][-1]['id']
        self.match_id = js['id']


    def set(self, set=None):
        if set == None:
            return self.info['set']
        self.info['set'] = set


    def team1(self, name=None):
        if name == None:
            return self.info['team1']
        self.info['team1'] = name.strip()
        self.info['t1_players'] = list(map(lambda x: x.strip(), self.info['team1'].split('/')))
        if len(self.info['t1_players']) == len(self.info['t2_players']):
            self.serving_order(sum(list(map(lambda x: [x,x+10], range(11,11+len(self.info['t1_players'])))), []))
        else:
            self.serving_order([0])


    def team2(self, name=None):
        if name == None:
            return self.info['team2']
        self.info['team2'] = name.strip()
        self.info['t2_players'] = list(map(lambda x: x.strip(), self.info['team2'].split('/')))
        if len(self.info['t1_players']) == len(self.info['t2_players']):
            self.serving_order(sum(list(map(lambda x: [x,x+10], range(11,11+len(self.info['t2_players'])))), []))
        else:
            self.serving_order([0])


    def referee(self, name=None):
        if name == None:
            return self.info['referee']
        else:
            self.info['referee'] = name


    def player(self, team, player):
        try:
            if team == 1:
                return self.info['t1_players'][player-1]
            if team == 2:
                return self.info['t2_players'][player-1]
        except:
            pass
        return None


    def team1_sets(self, sets=None):
        if sets == None:
            return self.info['team1_sets']
        self.info['team1_sets'] = sets


    def team1_score(self, score=None):
        if score == None:
            return self.info['team1_score']
        self.info['team1_score'] = score


    def team2_sets(self, sets=None):
        if sets == None:
            return self.info['team2_sets']
        self.info['team2_sets'] = sets


    def team2_score(self, score=None):
        if score == None:
            return self.info['team2_score']
        self.info['team2_score'] = score


    def server(self, server=None):
        if server == None:
            return self.info['server']
        self.serve_order[0] = server
        self.info['server'] = server
        try:
            team = int(server / 10)
            if server > 0 and self.serve_order[1] == 0:
                other_team = 2 if team == 1 else 1
                for i,v in enumerate(self.serve_order):
                    if v == 0 and i%2 == 0:
                        self.serve_order[i] = team * 10
                    if v == 0 and i%2 == 1:
                        self.serve_order[i] = other_team * 10
            if len(self.serve_order) == 4 and self.serve_order[2] == team * 10:
                if server == 11: self.serve_order[2] = 12
                if server == 12: self.serve_order[2] = 11
                if server == 21: self.serve_order[2] = 22
                if server == 22: self.serve_order[2] = 21
        except:
            pass


    def side_switch(self, switch=None):
        if switch == None:
            return self.switch_sides and not self.switch_sides_taken
        else:
            if switch:
                self.switch_sides_taken = self.switch_sides
                self.switch_sides = True
            else:
                self.switch_sides = False
                self.switch_sides_taken = False


    def team1_add_point(self):
        self.info['team1_score'] += 1
        if self.info['server'] in range(20,30):
            self.serve_order.rotate(-1)
            self.info['server'] = self.serve_order[0]


    def team2_add_point(self):
        self.info['team2_score'] += 1
        if self.info['server'] in range(10,20):
            self.serve_order.rotate(-1)
            self.info['server'] = self.serve_order[0]


    def team1_subtract_point(self):
        self.info['team1_score'] = max(0, self.info['team1_score'] - 1)


    def team2_subtract_point(self):
        self.info['team2_score'] = max(0, self.info['team2_score'] - 1)


    def serving_order(self, order):
        self.serve_order = deque(order)
