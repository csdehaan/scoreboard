#!/usr/bin/env python3

from time import sleep
from datetime import datetime, timedelta
from multiprocessing.connection import Client

from version import Version
from config import Config
from api import Api
from match import Match

import json
import threading
import subprocess
import socket
import sys

status = 'undefined'
next_match_teams = None

config = Config(sys.argv[1])
config.read()

api = Api(config.scoreboard["api_key"], config.scoreboard.getint('log_level', 20))
api.logger.info(f'Scoreboard {config.scoreboard["serial"]} Ver {Version.str()} Online')

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
api.logger.info(f'IP Address = {s.getsockname()[0]}')

sb = api.scoreboard()

court = str(sb['court'])
if court != config.scoreboard["court"]:
    config.scoreboard["court"] = court
    config.save()

def update_clock():
    global display
    global status

    if status == 'no_matches':
        threading.Timer(10, update_clock).start()
        display.send(['clock'])


def update_score():
    global display
    global match

    try:
        api.logger.debug(f'update_score: match={match.info}')
        display.send(['match', match])

    except Exception as e:
        api.logger.error(f'update_score exception: {e}')


def next_match_in(wait_time, teams):
    global next_match_teams
    next_match_teams = teams
    threading.Timer(wait_time, next_match_now).start()


def next_match_now():
    global next_match_teams
    global display
    global config
    global status

    countdown = config.scoreboard.getint('next_match_wait', 600)
    while countdown >= 0:
        if next_match_teams and status == 'selecting':
            display.send(['next_match', next_match_teams, countdown])
        countdown -= 1
        sleep(1)
    next_match_teams = None


def rx_score_update(message):
    global status
    global match
    global config

    api.logger.debug(f'rx_score_update: message={message}')

    try:
        m = json.loads(message)
        json2match(m, match)
        if m['state'] == 'in_progress':
            status = "scoring"
            update_score()
            if m['games'][-1]['game_over?']:
                status = "next_game"
        elif m['state'] == 'complete':
            matches = match_list()
            if len(matches['names']) > 0:
                api.logger.debug(f'rx_score_update: set_status_selecting')
                status = "selecting"
                update_score()
                next_match_in(config.scoreboard.getint('end_match_delay', 60), matches['teams'][0])
            else:
                api.logger.debug(f'rx_score_update: set_status_no_matches')
                status = "no_matches"
                update_clock()

    except Exception as e:
        api.logger.error(f'rx_score_update exception: {e}')


def rx_config_update(message):
    api.logger.info(f'rx_config_update: message={message}')

    try:
        m = json.loads(message)
        rc = subprocess.run(m['cmd'].split(' '), capture_output=True)
        api.logger.info(rc)
        

    except Exception as e:
        api.logger.error(f'rx_config_update exception: {e}')


def json2match(js, match):
    match.team1(js['team1_name'])
    match.team2(js['team2_name'])
    match.set(len(js['games']))
    match.team1_score(js['games'][-1]['team1_score'])
    match.team2_score(js['games'][-1]['team2_score'])
    match.server(js['games'][-1]['server_number'])
    match.game_id = js['games'][-1]['id']
    match.match_id = js['id']



def match_list():
    global api
    global status
    global match

    api.logger.debug(f'match_list')
    try:
        matches = api.matches()
        if len(matches) > 0:
            names = []
            ids = []
            teams = []
            for js_match in matches:
                if js_match['state'] == 'scheduled':
                    try:
                        names.append(f'{js_match["name"]}\t[{datetime.strptime(js_match["scheduled_time"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%H:%M")}]')
                        ids.append(js_match["id"])
                        teams.append([js_match['team1_name'],js_match['team2_name']])
                    except:
                        names.append(f'{js_match["name"]}\t')
                        ids.append(js_match["id"])
                        teams.append([js_match['team1_name'],js_match['team2_name']])
                if js_match['state'] == 'in_progress':
                    api.logger.debug(f'check_status_of_matches: match {js_match["id"]} in progress')
                    status = "scoring"
                    json2match(js_match, match)
                    update_score()
                    return False

            if len(names) > 0:
                api.logger.debug("check_status_of_matches: displaying menu to select match")
                return {'names': names, 'ids': ids, 'teams': teams}

    except Exception as e:
        api.logger.error(f'check_status_of_matches exception: {e}')

    return {'names': [], 'ids': [], 'teams': []}


display = Client(('localhost', 6000), authkey=b'vbscores')

match = Match()

api.logger.debug('Subscribing to score updates')
api.subscribe_score_updates(rx_score_update)

api.logger.debug('Subscribing to config updates')
api.subscribe_config_updates(rx_config_update)

matches = match_list()
api.logger.debug(f'scheduled matches: {matches}')
if matches:
    if len(matches['names']) > 0:
        api.logger.debug(f'set_status_selecting')
        status = "selecting"
        display.send(['next_match', matches['teams'][0], -1])
    else:
        status = "no_matches"
        update_clock()

# wait for display process to exit
sleep(1000)