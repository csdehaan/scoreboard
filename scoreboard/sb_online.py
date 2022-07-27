
from time import sleep
from datetime import datetime
from datetime import timedelta
import json
import threading
import subprocess
import socket
import traceback
from websocket import WebSocketTimeoutException
import logging

from scoreboard import Version, Match, Config
from scoreboard.controller import Controller
from scoreboard.api import Api
from scoreboard.display_connection import Display
from scoreboard.renogy import Renogy


class AckTimeout(Exception):
    pass

countdown = 0
display = None
config = None
api = None
controller = None
match = None
switching_sides = False
disconnected = False
renogy = None
timeout = None
next_match = None
timer = None


def ping_timeout(ws_app, error):
    global display
    global disconnected

    if isinstance(error, WebSocketTimeoutException):
        display.send(['mesg', 'Connecting ...'])
        disconnected = True


def periodic_task(interval, times = 1000000000, cleanup = None):
    def outer_wrap(function):
        def wrap(*args, **kwargs):
            stop = threading.Event()
            def inner_wrap():
                i = 0
                delta = timedelta(seconds=interval)
                start_time = datetime.now()
                while i < times and not stop.isSet():
                    function(i, *args, **kwargs)
                    i += 1
                    stop.wait((start_time + (delta * i) - datetime.now()).total_seconds())

                if cleanup:
                    cleanup()

            t = threading.Timer(0, inner_wrap)
            t.daemon = True
            t.start()
            return stop
        return wrap
    return outer_wrap


@periodic_task(1)
def update_timer(i, msg, seconds):
    global display
    global timer

    display.send(['timer', msg, seconds-i])
    if seconds-i <= 0:
        timer.set()
        timer = None



@periodic_task(1)
def update_next_match(i):
    global countdown
    global display
    global controller
    global disconnected
    global next_match
    global timer

    if timer: return

    try:
        if (i % 10 == 0) and (disconnected or controller.status() != 'scoring'):
            matches = match_list()
            if matches:
                if len(matches['names']) > 0:
                    api.logger.debug(f'set_status_selecting')
                    controller.set_status_selecting(matches)
                    next_match = matches['teams'][0]
                    display.send(['next_match', next_match, countdown])
                else:
                    next_match = None
                    countdown = 0
                    controller.set_status_no_matches()
                    display.send(['clock'])

        if next_match and countdown > 0 and (disconnected or controller.status() != 'scoring'):
            countdown -= 1
            display.send(['next_match', next_match, countdown])

    except Exception as e:
        api.logger.error(f'periodic_update exception: {traceback.format_exc()}')



def after_timeout():
    global timeout

    timeout = None
    match_list()


@periodic_task(1, 60, after_timeout)
def update_timeout(i, name):
    global display
    display.send(['mesg', name, 'TIMEOUT', str(60-i)])


def side_switch_clear():
    global switching_sides
    switching_sides = False
    update_score()



@periodic_task(10, 1, side_switch_clear)
def side_switch(i):
    global display
    global switching_sides

    switching_sides = True
    display.send(['mesg','SWITCH','SIDES'])


def update_score():
    global display
    global controller
    global match
    global switching_sides

    try:
        api.logger.debug(f'update_score: match={match.info}')
        if switching_sides == False: display.send(['match', match])
        controller.set_t1_name(match.team1())
        controller.set_t2_name(match.team2())
        controller.set_score(match.team1_score(), match.team2_score(), match.server())

    except Exception as e:
        api.logger.error(f'update_score exception: {traceback.format_exc()}')


def next_match_in(wait_time):
    global next_match
    next_match = None
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
    global display

    api.logger.debug(f'rx_score_update: message={message}')

    try:
        m = json.loads(message)
        json2match(m, match)
        if m['state'] == 'in_progress':
            controller.set_status_scoring()
            if m['games'][-1]['switch_sides?']:
                side_switch()
            update_score()
            if m['games'][-1]['game_over?']:
                controller.set_status_next_game()
        elif m['state'] == 'complete':
            update_score()
            next_match_in(config.scoreboard.getint('end_match_delay', 60))

    except Exception as e:
        api.logger.error(f'rx_score_update exception: {traceback.format_exc()}')


def rx_config_update(message):
    global display
    global timeout
    global timer

    api.logger.info(f'rx_config_update: message={message}')

    try:
        m = json.loads(message)
        cmd = m.get('cmd')
        if cmd:
            rc = subprocess.run(cmd.split(' '), capture_output=True)
            api.logger.info(rc)
        cmd = m.get('start_timeout')
        if cmd:
            timeout = update_timeout(cmd)
        cmd = m.get('end_timeout')
        if cmd:
            if timeout:
                timeout.set()
        cmd = m.get('start_timer')
        if cmd:
            if timer: timer.set()
            timer = update_timer(m.get('timer_msg'), int(cmd))


    except Exception as e:
        api.logger.error(f'rx_config_update exception: {traceback.format_exc()}')


def json2match(js, match):
    match.team1(js['team1_name'])
    match.team2(js['team2_name'])
    match.set(len(js['games']))
    match.team1_sets(js['games_team1'])
    match.team2_sets(js['games_team2'])
    match.team1_score(js['games'][-1]['team1_score'])
    match.team2_score(js['games'][-1]['team2_score'])
    match.server(js['games'][-1]['server_number'])
    match.game_id = js['games'][-1]['id']
    match.match_id = js['id']



def match_list():
    global api
    global controller
    global match
    global disconnected

    api.logger.debug(f'match_list')
    try:
        matches = api.matches()
        if disconnected:
            if api.connection.connected: api.connection.disconnect()
            api.connection.connect()
            disconnected = False
        if len(matches) > 0:
            names = []
            ids = []
            teams = []
            for js_match in matches:
                if js_match['state'] == 'scheduled':
                    try:
                        names.append(f'{js_match["name"]}\t[{datetime.strptime(js_match["scheduled_time"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%H:%M")}]')
                        ids.append(js_match["id"])
                        ref = 'TBD' if js_match['ref_name'] == '' else js_match['ref_name']
                        teams.append([js_match['team1_name'],js_match['team2_name'],ref])
                    except:
                        names.append(f'{js_match["name"]}\t')
                        ids.append(js_match["id"])
                        ref = 'TBD' if js_match['ref_name'] == '' else js_match['ref_name']
                        teams.append([js_match['team1_name'],js_match['team2_name'],ref])
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
        api.logger.error(f'check_status_of_matches exception: {traceback.format_exc()}')

    return {'names': [], 'ids': [], 'teams': []}



@periodic_task(30)
def update_status(i):
    global api
    global renogy

    status = {}
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as sensor:
            temperature = int(sensor.readline()) / 1000.0
            status["cpu_temperature"] = temperature
            if temperature > 58:
                api.logger.warning(f'CPU Temperature = {temperature}')
    except:
        pass

    try:
        if renogy:
            renogy.read()
            status["batt_charge"] = renogy.batt_soc
            status["load_watts"] = renogy.load_watts
            status["pv_watts"] = renogy.pv_watts
    except:
        pass

    try:
        api.scoreboard_status(status)
    except:
        pass


def bt_button(value, options):
    global api
    global controller
    global match
    global config

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
    if value[0] == 97:
        controller.send_config(config.json())
    if value[0] == 98:
        try:
            value.pop(0)
            config_setting = json.loads(bytes(value).decode('utf8'))
            config.config[config_setting[0]][config_setting[1]] = config_setting[2]
            config.save()
        except:
            api.logger.error(f'failed to make config change from: {bytes(value).decode("utf8")}')



def sb_online(configfile=None):
    global api
    global controller
    global match
    global countdown
    global config
    global display
    global renogy

    restart_display = False

    config = Config(configfile)
    config.read()

    display = Display('localhost', config.display.getint("port", 6000))

    api = Api(config.scoreboard["api_key"], config.scoreboard.getint('log_level', logging.WARNING), ping_timeout)
    api.logger.info(f'Scoreboard {config.scoreboard["serial"]} Ver {Version.str()} Online')

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    api.logger.info(f'IP Address = {s.getsockname()[0]}')

    sb = api.scoreboard()
    logo_img = sb["organization"]["abbrev"]
    if logo_img != config.display.get("logo", logo_img):
        config.display["logo"] = logo_img
        config.save()
        restart_display = True

    court = str(sb['court'])
    if court != config.scoreboard["court"]:
        config.scoreboard["court"] = court
        config.save()
        restart_display = True

    if restart_display:
        display.send(['shutdown'])
        sleep(1)

    api.logger.debug('Enabling bluetooth')
    controller = Controller(f'SB {config.scoreboard["serial"]}', bt_button)

    match = Match()

    api.logger.debug('Subscribing to score updates')
    api.subscribe_score_updates(rx_score_update)

    api.logger.debug('Subscribing to config updates')
    api.subscribe_config_updates(rx_config_update)

    renogy_port = config.scoreboard.get("renogy_port")
    renogy_baud = config.scoreboard.getint("renogy_baud", 9600)
    renogy_addr = config.scoreboard.getint("renogy_addr", 255)
    if renogy_port:
        renogy = Renogy(renogy_port, renogy_baud, renogy_addr)

    update_next_match()
    update_status()

    controller.publish()
