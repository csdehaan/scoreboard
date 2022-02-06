
from time import sleep
from datetime import datetime, timedelta
from multiprocessing.connection import Client

from scoreboard import Version, Match, Config
from scoreboard.controller import Controller
from scoreboard.api import Api

import json
import threading
import subprocess
import socket
import sys

restart_display = False
countdown = 0
display = None
config = None
api = None
controller = None
match = None


def periodic_update():
    global countdown
    global display
    global controller

    threading.Timer(10, periodic_update).start()
    if countdown > 0: countdown -= 10
    if controller.status() != 'scoring':
        matches = match_list()
        if matches:
            if len(matches['names']) > 0:
                api.logger.debug(f'set_status_selecting')
                controller.set_status_selecting(matches)
                display.send(['next_match', matches['teams'][0], countdown])
            else:
                controller.set_status_no_matches()
                display.send(['clock'])


def update_score():
    global display
    global controller
    global match

    try:
        api.logger.debug(f'update_score: match={match.info}')
        display.send(['match', match])
        controller.set_t1_name(match.team1())
        controller.set_t2_name(match.team2())
        controller.set_score(match.team1_score(), match.team2_score(), match.server())

    except Exception as e:
        api.logger.error(f'update_score exception: {e}')


def next_match_in(wait_time):
    threading.Timer(wait_time, next_match_now).start()


def next_match_now():
    global countdown
    global controller
    global config

    controller.set_status_waiting()
    countdown = config.scoreboard.getint('next_match_wait', 600)


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
            if m['games'][-1]['switch_sides?']:
                display.send(['mesg','SWITCH','SIDES'])
                sleep(5)
            update_score()
            if m['games'][-1]['game_over?']:
                controller.set_status_next_game()
        elif m['state'] == 'complete':
            update_score()
            next_match_in(config.scoreboard.getint('end_match_delay', 60))

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



def sb_online():
    global api
    global controller
    global match
    global countdown
    global config
    global display

    config = Config()
    config.read()

    api = Api(config.scoreboard["api_key"], config.scoreboard.getint('log_level', 20))
    api.logger.info(f'Scoreboard {config.scoreboard["serial"]} Ver {Version.str()} Online')

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    api.logger.info(f'IP Address = {s.getsockname()[0]}')

    sb = api.scoreboard()
    logo_img = sb["organization"]["abbrev"]
    if logo_img != config.display["logo"]:
        config.display["logo"] = logo_img
        config.save()
        restart_display = True

    court = str(sb['court'])
    if court != config.scoreboard["court"]:
        config.scoreboard["court"] = court
        config.save()
        restart_display = True

    while display == None:
        try:
            display = Client(('localhost', config.display.getint("port", 6000)), authkey=b'vbscores')
            if restart_display:
                display.send(['shutdown'])
                sys.exit(0)
        except socket.error:
            sleep(0.25)

    api.logger.debug('Enabling bluetooth')
    controller = Controller(f'SB {config.scoreboard["serial"]}', bt_button)

    match = Match()

    api.logger.debug('Subscribing to score updates')
    api.subscribe_score_updates(rx_score_update)

    api.logger.debug('Subscribing to config updates')
    api.subscribe_config_updates(rx_config_update)

    periodic_update()
    log_cpu_temperature()

    controller.publish()

