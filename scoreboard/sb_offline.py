
from time import sleep
from datetime import datetime
from datetime import timedelta
from pynput import keyboard
from collections import deque
import threading
import re
import evdev

from scoreboard import Scoreboard

scoreboard = Scoreboard()
stdinput = deque()
timer = None
timer_running = False
timer_count = 0


def on_keypress(key):
    global stdinput
    try:
        stdinput.append(key.char)
    except AttributeError:
        if key == keyboard.Key.enter: stdinput.append('enter')
        if key == keyboard.Key.esc: stdinput.append('esc')
        if key == keyboard.Key.backspace: stdinput.append('backspace')
        if key == keyboard.Key.delete: stdinput.append('backspace')
        if key == keyboard.Key.down: stdinput.append('down')
        if key == keyboard.Key.up: stdinput.append('up')

def select_device(paths):
    dev, count = None, 0
    for path in paths:
        try:
            next_dev = evdev.InputDevice(path)
        except OSError:
            continue

        # Does this device provide more handled event codes?
        capabilities = next_dev.capabilities()
        cap = capabilities[1]
        next_count = len(cap)
        if next_count > count and 30 in cap and 48 in cap:
            dev = path
            count = next_count
        next_dev.close()

    return dev



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
    global timer_running
    global timer_count

    if timer_running:
        if seconds > 0: timer_count -= 1
        else: timer_count += 1
    if timer_count < 0:
        timer_running = False
    else:
        scoreboard.timer(msg, timer_count)


@periodic_task(10)
def update_clock(i):
    global scoreboard
    scoreboard.update_clock()


def update_score():
    global scoreboard
    scoreboard.update_score()


def get_key(filter=None):
    global stdinput
    while True:
        try:
            key = stdinput.popleft()
            if filter:
                if re.fullmatch(filter, key): return key
            else:
                return key
        except IndexError:
            sleep(0.1)
        except:
            return ''


def get_input(prompt, accept_key = 'enter', cancel_key = 'esc'):
    global scoreboard
    global stdinput

    stdinput.clear()
    input = ''
    while True:
        scoreboard.message(prompt, input)
        key = get_key(f'\S|{accept_key}|{cancel_key}|backspace')
        if key == accept_key: return input
        if key == cancel_key: return None
        if key == 'backspace': input = input[:-1]
        else: input += key


def assign_server():
    global scoreboard
    try:
        team = int(get_key())
        if team != 1 and team != 2: return
        player = int(get_key())
        if player < 1 or player > 4: return
        server = team * 10 + player
        scoreboard.match.serve_order[0] = server
        scoreboard.match.server(server)
    except:
        pass


def next_set():
    global scoreboard
    try:
        if scoreboard.match.team1_score() > scoreboard.match.team2_score():
            scoreboard.match.team1_sets(scoreboard.match.team1_sets() + 1)
            if scoreboard.match.team1_sets() < 2:
                scoreboard.match.team1_score(0)
                scoreboard.match.team2_score(0)
                scoreboard.match.serving_order(sum(list(map(lambda x: [0,0], range(11,11+len(scoreboard.match.info['t1_players'])))), []))
                scoreboard.match.server(0)
        else:
            scoreboard.match.team2_sets(scoreboard.match.team2_sets() + 1)
            if scoreboard.match.team2_sets() < 2:
                scoreboard.match.team1_score(0)
                scoreboard.match.team2_score(0)
                scoreboard.match.serving_order(sum(list(map(lambda x: [0,0], range(11,11+len(scoreboard.match.info['t1_players'])))), []))
                scoreboard.match.server(0)
    except:
        pass


def start_game():
    global scoreboard

    scoreboard.set_mode_menu()
    t1 = get_input('Team 1 Name:')
    if t1:
        t2 = get_input('Team 2 Name:')
        if t2:
            scoreboard.match.reset()
            scoreboard.match.team1(t1)
            scoreboard.match.team2(t2)
            scoreboard.match.serving_order(sum(list(map(lambda x: [0,0], range(11,11+len(scoreboard.match.info['t1_players'])))), []))
            scoreboard.match.server(0)
            scoreboard.set_mode_score()
            update_score()
            while True:
                key = get_key()
                if key == '1': scoreboard.match.team1_add_point()
                if key == '2': scoreboard.match.team2_add_point()
                if key == '!': scoreboard.match.team1_subtract_point()
                if key == '@': scoreboard.match.team2_subtract_point()
                if key == 's': assign_server()
                if key == 'n': next_set()
                if key == 'esc': return
                update_score()


def stopwatch():
    global scoreboard
    global timer
    global timer_running
    global timer_count

    try:
        scoreboard.set_mode_menu()
        if timer: timer.set()
        timer_running = False
        timer_count = 0
        timer = update_timer('', -1)
        while True:
            key = get_key()
            if key == 'r':
                timer_count = 0
            if key == 'enter':
                timer_running = not timer_running
            if key == 'esc':
                if timer: timer.set()
                timer = None
                return
    except:
        if timer: timer.set()
        timer = None


def countdown_timer():
    global scoreboard
    global timer
    global timer_running
    global timer_count

    try:
        scoreboard.set_mode_menu()
        if timer: timer.set()
        timer_running = False
        countdown = get_input('Countdown Time:')
        min_sec = countdown.split(':', 1)
        if len(min_sec) == 1: timer_count = int(min_sec[0])
        else: timer_count = int(min_sec[0]) * 60 + int(min_sec[1])
        timer = update_timer('', timer_count)
        while True:
            key = get_key()
            if key == 'r':
                if len(min_sec) == 1: timer_count = int(min_sec[0])
                else: timer_count = int(min_sec[0]) * 60 + int(min_sec[1])
            if key == 'enter':
                timer_running = not timer_running
            if key == 'esc':
                if timer: timer.set()
                timer = None
                return
    except:
        if timer: timer.set()
        timer = None



def show_status():
    global stdinput
    while True:
        cpu = 'UNK'
        try:
            cpu = round(scoreboard.cpu_temperature(), 1)
        except:
            pass
        wifi = 'UNK'
        try:
            wifi = scoreboard.wifi_signal()
        except:
            pass
        scoreboard.message('STATUS:', '', f'CPU Temp = {cpu}', f'WiFi Signal = {wifi}')
        if len(stdinput) > 0:
            key = stdinput.popleft()
            if key == 'esc': return
        sleep(0.5)


def config_wifi():
    global scoreboard

    scoreboard.set_mode_menu()
    ssid = get_input('Enter WiFi SSID:')
    if ssid:
        pw = get_input('Enter Password:')
        if pw:
            scoreboard.config.wifi['ssid'] = ssid
            scoreboard.config.wifi['password'] = pw
            scoreboard.config.save()


def set_brightness():
    global scoreboard

    try:
        scoreboard.set_mode_menu()
        brightness = get_input('Brightness:')
        if brightness: scoreboard.set_brightness(brightness)
    except:
        pass


def set_court():
    global scoreboard

    try:
        scoreboard.set_mode_menu()
        court = get_input('Court:')
        if court:
            court = int(court)
            if court > 0 and court < 1000:
                scoreboard.set_court(court)
    except:
        pass


def set_end_delay():
    global scoreboard

    try:
        scoreboard.set_mode_menu()
        delay = get_input('Match End Delay:')
        if delay:
            delay = int(delay)
            if delay >= 0 and delay <= 1000:
                scoreboard.config.scoreboard['end_match_delay'] = str(delay)
                scoreboard.config.save()
    except:
        pass


def set_next_delay():
    global scoreboard

    try:
        scoreboard.set_mode_menu()
        delay = get_input('Next Match Delay:')
        if delay:
            delay = int(delay)
            if delay >= 0 and delay <= 5000:
                scoreboard.config.scoreboard['next_match_wait'] = str(delay)
                scoreboard.config.save()
    except:
        pass


menu = [['Start Match',start_game], ['Stopwatch',stopwatch], ['Timer',countdown_timer], ['Show Status', show_status], ['Config WiFi',config_wifi], ['Brightness', set_brightness], ['Court Number', set_court], ['Match End Delay', set_end_delay], ['Next Match Delay', set_next_delay]]


def menu_item(idx, sel):
    global menu
    if sel == idx: return [menu[idx][0],(0,255,0)]
    return menu[idx][0]


def show_menu(idx):
    global scoreboard
    global menu
    scoreboard.set_mode_menu()
    max = len(menu)
    r1 = range(0,2)
    r2 = range(2,max-3)
    r3 = range(max-3,max)
    m = []
    if idx in r1:
        m.append(menu_item(0, idx))
        m.append(menu_item(1, idx))
        m.append(menu_item(2, idx))
        m.append(menu_item(3, idx))
    if idx in r2:
        m.append(menu_item(idx-1, idx))
        m.append(menu_item(idx, idx))
        m.append(menu_item(idx+1, idx))
        m.append(menu_item(idx+2, idx))
    if idx in r3:
        m.append(menu_item(len(menu)-4, idx))
        m.append(menu_item(len(menu)-3, idx))
        m.append(menu_item(len(menu)-2, idx))
        m.append(menu_item(len(menu)-1, idx))
    scoreboard.message(m[0], m[1], m[2], m[3])


def do_menu(idx=0):
    while True:
        show_menu(idx)
        key = get_key()
        if key == 'down':
            if idx < len(menu) - 1: idx += 1
        if key == 'up':
            if idx > 0: idx -= 1
        if key == 'enter':
            menu[idx][1]()
            return
        if key == 'esc':
            return


def sb_offline(configfile=None):
    global scoreboard

    scoreboard.set_config(configfile)
    scoreboard.open_display()
    update_clock()

    dev = select_device(evdev.list_devices())
    listener = keyboard.Listener(on_press=on_keypress, device_paths=[dev])
    listener.start()

    while True:
        key = get_key()
        if key == 'm': start_game()
        if key == 's': stopwatch()
        if key == 't': countdown_timer()
        if key == 'w': config_wifi()
        if key == 'up': do_menu()
        if key == 'down': do_menu()
        scoreboard.set_mode_clock()
        scoreboard.update_clock()


if __name__ == "__main__":
    import sys
    try:
        sb_offline(sys.argv[1])
    except IndexError:
        sb_offline()