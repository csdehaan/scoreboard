#!/usr/bin/env python3

from time import sleep
from datetime import datetime, timedelta

from config import Config
from display import Display
from controller import Controller
from api import Api
from match import Match

import json
import threading
import subprocess
import socket

config = Config()
config.read()

api = Api(config.scoreboard["api_key"], config.scoreboard.getint('log_level', 20))

api.logger.info(f'Scoreboard {config.scoreboard["serial"]} Online')

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
api.logger.info(f'IP Address = {s.getsockname()[0]}')

next_match_teams = None

def update_clock():
    global display
    global controller

    if controller.status() == 'no_matches':
        threading.Timer(10, update_clock).start()
        display.update_clock()


def update_score():
    global display
    global controller
    global match

    try:
        api.logger.debug(f'update_score: match={match.info}')
        display.update_match(match)
        controller.set_t1_name(match.team1())
        controller.set_t2_name(match.team2())
        controller.set_score(match.team1_score(), match.team2_score(), match.server())

    except Exception as e:
        api.logger.error(f'update_score exception: {e}')


def next_match_in(wait_time, teams):
    global next_match_teams
    next_match_teams = teams
    threading.Timer(wait_time, next_match_now).start()


def next_match_now():
    global next_match_teams
    global display
    global controller
    global config

    countdown = config.scoreboard.getint('next_match_wait', 600)
    while countdown >= 0:
        if next_match_teams and controller.status() == 'selecting':
            display.update_next_match(next_match_teams, countdown)
        countdown -= 1
        sleep(1)
    next_match_teams = None


def rx_score_update(message):
    global controller
    global match
    global config

    api.logger.debug(f'rx_score_update: message={message}')

    try:
        m = json.loads(message)
        json2match(m, match)
        if m['state'] == 'in_progress':
            controller.set_status_scoring()
            update_score()
            if m['games'][-1]['game_over?']:
                controller.set_status_next_game()
        elif m['state'] == 'complete':
            matches = match_list()
            if len(matches['names']) > 0:
                api.logger.debug(f'rx_score_update: set_status_selecting')
                controller.set_status_selecting(matches)
                update_score()
                next_match_in(config.scoreboard.getint('end_match_delay', 60), matches['teams'][0])
            else:
                api.logger.debug(f'rx_score_update: set_status_no_matches')
                controller.set_status_no_matches()
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
    global controller
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
                    controller.set_status_scoring()
                    json2match(js_match, match)
                    update_score()
                    return False

            if len(names) > 0:
                api.logger.debug("check_status_of_matches: displaying menu to select match")
                return {'names': names, 'ids': ids, 'teams': teams}

    except Exception as e:
        api.logger.error(f'check_status_of_matches exception: {e}')

    return {'names': [], 'ids': [], 'teams': []}



def log_cpu_temperature():
    global api

    threading.Timer(300, log_cpu_temperature).start()
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as sensor:
        temperature = int(sensor.readline()) / 1000.0
        api.logger.info(f'CPU Temperature = {temperature}')


def bt_button(value, options):
    global api
    global controller
    global match

    api.logger.debug(f'bt_button: value={value}')
    if value[0] == 49:
        api.team1_plus(match.game_id)
    if value[0] == 50:
        api.logger.debug('center button pressed')
    if value[0] == 51:
        api.team2_plus(match.game_id)
    if value[0] == 53:
        api.team1_minus(match.game_id)
    if value[0] == 54:
        if controller.status() == 'scoring':
            api.end_game(match.game_id)
    if value[0] == 55:
        api.team2_minus(match.game_id)
    if value[0] == 74:
        api.start_game(match.match_id)
    if value[0] == 75:
        api.end_match(match.match_id)
    if value[0] == 82:
        matches = match_list()
        if matches:
            api.logger.debug(f'set_status_selecting')
            controller.set_status_selecting(matches)
    if value[0] == 83:
        value.pop(0)
        match_id = ''.join([chr(item) for item in value])
        api.start_game(match_id)
    if value[0] == 79:
        api.logger.debug(f'set_status_serve order')
        serving_order = api.get_serving_order(match.game_id)
        controller.set_status_serve_order(serving_order)
    if value[0] == 80:
        value.pop(0)
        if len(value) > 0:
            api.logger.debug(f'set serving order {value}')
            api.set_serving_order(match.game_id, ''.join([chr(item) for item in value]))
        else:
            api.logger.debug('cancel set serving order')
        controller.set_status_scoring()


sb = api.scoreboard()
display = Display(config, f'{sb["organization"]["abbrev"]}.png', sb['court'])

api.logger.debug('Enabling bluetooth')
controller = Controller(f'SB {config.scoreboard["serial"]}', bt_button)

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
        controller.set_status_selecting(matches)
        display.update_next_match(matches['teams'][0])
    else:
        controller.set_status_no_matches()
        update_clock()

log_cpu_temperature()

controller.publish()

