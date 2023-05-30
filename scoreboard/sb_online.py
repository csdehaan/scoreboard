
from time import sleep
from datetime import datetime
from datetime import timedelta
import json
import threading
import subprocess
import socket
from websocket import WebSocketTimeoutException
import logging

from scoreboard import Version, Scoreboard
from scoreboard.api import Api
from scoreboard.renogy import Renogy
from scoreboard.workout import Workout
from scoreboard.gpio import GPIO


class AckTimeout(Exception):
    pass

scoreboard = Scoreboard()

countdown = 0
countdown_timer = None
api = None
switching_sides = False
renogy = None
timeout = None
next_match = None
timer = None
workout = None
gpio = None


def ping_timeout(ws_app, error):
    global scoreboard

    if isinstance(error, WebSocketTimeoutException):
        scoreboard.message('Connecting ...')
        scoreboard.set_disconnected()
        api.logger.warning('Ping Timeout')


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
    global scoreboard
    global timer

    time = 0
    if seconds > 0: time = seconds-i
    else: time = i+1
    scoreboard.timer(msg, time)
    if time <= 0:
        timer.set()
        timer = None


@periodic_task(1)
def update_workout(i, workout):
    global timer

    if workout.resting:
        if workout.exercise_rest() < 0:
            scoreboard.message(workout.exercise_name(), f'SET: {workout.current_set}', 'REST')
        else:
            scoreboard.message(workout.exercise_name(), f'SET: {workout.current_set}', f'REST: {workout.time_remaining()}')

    elif workout.exercise_type() == 'repetitions':
        scoreboard.message(workout.exercise_name(), f'SET: {workout.current_set}', f'REPS: {workout.exercise_target()}')
    elif workout.exercise_type() == 'duration':
        scoreboard.message(workout.exercise_name(), f'SET: {workout.current_set}', f'TIME: {workout.time_remaining()}')
    elif workout.exercise_type() == 'rest':
        scoreboard.message(workout.exercise_name(), f'TIME: {workout.time_remaining()}')
    workout.tick()

    if workout.in_progress() == False and timer != None:
        timer.set()
        timer = None



@periodic_task(15)
def update_next_match(i):
    global scoreboard
    global countdown
    global next_match
    global timer

    if timer: return

    try:
        api.logger.debug(f'update_next_match: scoreboard mode = {scoreboard.mode}')
        if (scoreboard.is_disconnected() or scoreboard.mode != 'score'):
            next_match = get_next_match_teams()
            api.logger.debug(f'update_next_match next match = {next_match}')
            if next_match == False:
                scoreboard.set_mode_score()
            elif len(next_match) > 0:
                scoreboard.next_match(next_match[0], next_match[1], next_match[2], countdown)
            elif scoreboard.is_connected():
                countdown = 0
                scoreboard.set_mode_clock()
                scoreboard.update_clock()

    except Exception as e:
        api.logger.error(f'update_next_match exception: {type(e).__name__} - {e}')


@periodic_task(1)
def update_next_match_countdown(i):
    global scoreboard
    global countdown
    global countdown_timer
    global next_match
    global timer

    countdown -= 1
    if next_match and countdown > 0 and (scoreboard.is_disconnected() or scoreboard.mode != 'score'):
        scoreboard.next_match(next_match[0], next_match[1], next_match[2], countdown)

    if countdown <= 0:
        countdown_timer.set()
        countdown_timer = None



def after_timeout():
    global timeout
    timeout = None
    update_score()



@periodic_task(1, 1000, after_timeout)
def update_timeout(i, name, length=60):
    global scoreboard
    global timeout

    count = length-i
    if length > 60:
        msg = f'{int(count/60)}:{(int(count)%60):02}'
    else:
        msg = str(count)
    scoreboard.message(name, 'TIMEOUT', msg)
    if count <= 0 and timeout: timeout.set()


def side_switch_clear():
    global switching_sides
    switching_sides = False
    update_score()



@periodic_task(10, 1, side_switch_clear)
def side_switch(i):
    global scoreboard
    global switching_sides
    switching_sides = True
    scoreboard.message('SWITCH','SIDES')


def update_score():
    global scoreboard
    global switching_sides

    try:
        api.logger.debug(f'update_score: match={scoreboard.match.info}')
        if switching_sides == False: scoreboard.update_score()

    except Exception as e:
        api.logger.error(f'update_score exception: {type(e).__name__} - {e}')


def next_match_in(wait_time):
    global next_match
    next_match = None
    threading.Timer(wait_time, next_match_now).start()


def next_match_now():
    global scoreboard
    global countdown
    global countdown_timer

    if countdown_timer == None:
        scoreboard.set_mode_next_match()
        countdown = scoreboard.config.scoreboard.getint('next_match_wait', 600)
        countdown_timer = update_next_match_countdown()


def rx_score_update(message):
    global scoreboard

    api.logger.debug(f'rx_score_update: message={message}')

    try:
        m = json.loads(message)
        scoreboard.match.from_json(m)
        if m['state'] == 'in_progress':
            scoreboard.set_mode_score()
            update_score()
            if scoreboard.match.side_switch():
                sleep(1)
                side_switch()
        elif m['state'] == 'complete':
            update_score()
            next_match_in(scoreboard.config.scoreboard.getint('end_match_delay', 60))

    except Exception as e:
        api.logger.error(f'rx_score_update exception: {type(e).__name__} - {e}')


def rx_config_update(message):
    global api
    global timeout
    global timer
    global workout
    global scoreboard

    api.logger.debug(f'rx_config_update: message={message}')

    try:
        m = json.loads(message)
        cmd = m.get('cmd')
        if cmd:
            rc = subprocess.run(cmd.split(' '), capture_output=True)
            api.logger.info(rc)
        cmd = m.get('start_timeout')
        if cmd and timeout == None:
            if cmd == 'MEDICAL': timeout = update_timeout(cmd, 300)
            else: timeout = update_timeout(cmd)
        cmd = m.get('end_timeout')
        if cmd:
            if timeout:
                timeout.set()
        cmd = m.get('start_timer')
        if cmd:
            if timer: timer.set()
            time = int(cmd)
            if time != 0: timer = update_timer(m.get('timer_msg'), time)
        cmd = m.get('workout')
        if cmd:
            if (workout == None) or (workout and not workout.in_progress()):
                if timer: timer.set()
                workout = Workout(m.get('workout'))
                workout.start()
                timer = update_workout(workout)
        cmd = m.get('ctrl_workout')
        if cmd and workout:
            if cmd == 'stop':
                if timer: timer.set()
                timer = None
                workout = None
            if cmd == 'pause':
                workout.pause()
            if cmd == 'step':
                if workout.resting: workout.next_set()
                else: workout.finish_set()
            if cmd == 'back':
                workout.previous_set()
        cmd = m.get('brightness')
        if cmd:
            scoreboard.set_brightness(cmd)
        cmd = m.get('set_mode')
        if cmd:
            scoreboard.mode = cmd
            scoreboard.update_clock()


    except Exception as e:
        api.logger.error(f'rx_config_update exception: {type(e).__name__} - {e}')



def match_list():
    global api
    global scoreboard

    api.logger.debug('match_list')
    try:
        if scoreboard.is_disconnected():
            # if api.connection.connected: api.connection.disconnect()
            # api.connection.connect()
            scoreboard.set_connected()
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
                        ref = 'TBD' if js_match['ref_name'] == '' else js_match['ref_name']
                        teams.append([js_match['team1_name'],js_match['team2_name'],ref])
                    except:
                        names.append(f'{js_match["name"]}\t')
                        ids.append(js_match["id"])
                        ref = 'TBD' if js_match['ref_name'] == '' else js_match['ref_name']
                        teams.append([js_match['team1_name'],js_match['team2_name'],ref])
                if js_match['state'] == 'in_progress':
                    api.logger.debug(f'check_status_of_matches: match {js_match["id"]} in progress')
                    scoreboard.set_mode_score()
                    scoreboard.match.from_json(js_match)
                    update_score()
                    return False

            if len(names) > 0:
                api.logger.debug("check_status_of_matches: displaying menu to select match")
                return {'names': names, 'ids': ids, 'teams': teams}

    except Exception as e:
        api.logger.error(f'check_status_of_matches exception: {type(e).__name__} - {e}')

    return {'names': [], 'ids': [], 'teams': []}



def get_next_match_teams():
    global api
    global scoreboard

    api.logger.debug('get_next_match_teams')
    try:
        if scoreboard.is_disconnected():
            # if api.connection.connected: api.connection.disconnect()
            # api.connection.connect()
            scoreboard.set_connected()
        next_match = api.next_match()
        if next_match:
            teams = []
            if next_match['state'] == 'scheduled':
                try:
                    ref = 'TBD' if next_match['ref_name'] == '' else next_match['ref_name']
                    teams = [next_match['team1_name'],next_match['team2_name'],ref]
                except:
                    pass
            if next_match['state'] == 'in_progress':
                api.logger.debug(f'get_next_match_teams: match {next_match["id"]} in progress')
                scoreboard.set_mode_score()
                scoreboard.match.from_json(next_match)
                update_score()
                return False

            if len(teams) > 0:
                api.logger.debug(f'get_next_match_teams: {teams}')
                return teams

    except Exception as e:
        scoreboard.message('Connecting ...')
        scoreboard.set_disconnected()
        api.logger.error(f'get_next_match_teams exception: {type(e).__name__} - {e}')

    return []



@periodic_task(30)
def update_status(i):
    global scoreboard
    global api
    global renogy
    global gpio

    status = {}
    try:
        temperature = scoreboard.cpu_temperature()
        status["cpu_temperature"] = temperature
        if temperature > 70:
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
        status["fan_alert"] = gpio.fan_alert()
        if status["fan_alert"]:
            gpio.fan_alert_clear()
    except:
        pass

    try:
        status["wifi"] = scoreboard.wifi_signal()
    except:
        pass

    try:
        status["vol"] = scoreboard.volume()
    except:
        pass

    try:
        api.scoreboard_status(status)
    except:
        pass


def sb_online(configfile=None):
    global api
    global scoreboard
    global renogy
    global gpio

    restart_display = False

    scoreboard.set_config(configfile)
    scoreboard.open_display()

    api = Api(scoreboard.config.scoreboard["api_key"], scoreboard.config.scoreboard.getint('log_level', logging.WARNING), ping_timeout)
    api.logger.info(f'Scoreboard {scoreboard.config.scoreboard["serial"]} Ver {Version.str()} Online')

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    api.logger.info(f'IP Address = {s.getsockname()[0]}')

    sb = api.scoreboard()
    logo_img = sb["organization"]["abbrev"]
    if logo_img != scoreboard.config.display.get("logo", logo_img):
        scoreboard.config.display["logo"] = logo_img
        scoreboard.config.save()
        restart_display = True

    court = str(sb['court'])
    if court != scoreboard.config.scoreboard["court"]:
        scoreboard.config.scoreboard["court"] = court
        scoreboard.config.save()
        restart_display = True

    if restart_display:
        scoreboard.display.send(['shutdown'])
        sleep(1)

    api.logger.debug('Subscribing to score updates')
    api.subscribe_score_updates(rx_score_update)

    api.logger.debug('Subscribing to config updates')
    api.subscribe_config_updates(rx_config_update)

    renogy_port = scoreboard.config.scoreboard.get("renogy_port")
    renogy_baud = scoreboard.config.scoreboard.getint("renogy_baud", 9600)
    renogy_addr = scoreboard.config.scoreboard.getint("renogy_addr", 255)
    if renogy_port:
        renogy = Renogy(renogy_port, renogy_baud, renogy_addr)

    gpio = GPIO(scoreboard.config)

    update_next_match()
    update_status()

    while True: sleep(1)
