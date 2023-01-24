
from time import sleep
from pynput import keyboard
from collections import deque
import threading
import re

from scoreboard import Scoreboard

scoreboard = Scoreboard()
stdinput = deque()


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


def update_clock():
    global scoreboard

    threading.Timer(10, update_clock).start()
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
        print(scoreboard.match.serve_order)
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
                if key == '1':
                    scoreboard.match.team1_add_point()
                    print(scoreboard.match.serve_order)
                if key == '2':
                    scoreboard.match.team2_add_point()
                    print(scoreboard.match.serve_order)
                if key == '!': scoreboard.match.team1_subtract_point()
                if key == '@': scoreboard.match.team2_subtract_point()
                if key == 's': assign_server()
                if key == 'n': next_set()
                if key == 'esc':
                    return
                update_score()


def show_status():
    global stdinput
    while True:
        cpu = 'UNK'
        try:
            cpu = scoreboard.cpu_temperature()
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
        if brightness:
            brightness = int(brightness)
            if brightness >= 0 and brightness <= 100:
                scoreboard.config.display['brightness'] = str(brightness)
                scoreboard.config.save()
                scoreboard.restart_display()
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


menu = [['Start Match',start_game], ['Show Status', show_status], ['Config WiFi',config_wifi], ['Brightness', set_brightness], ['Court Number', set_court], ['Match End Delay', set_end_delay], ['Next Match Delay', set_next_delay]]


def menu_item(idx, sel):
    if sel == idx: return [menu[idx][0],(0,255,0)]
    return menu[idx][0]


def show_menu(idx):
    global scoreboard
    scoreboard.set_mode_menu()
    r1 = range(0,2)
    r2 = range(2,4)
    r3 = range(4,7)
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

    listener = keyboard.Listener(on_press=on_keypress)
    listener.start()

    while True:
        key = get_key()
        if key == 'w': config_wifi()
        if key == 'm': start_game()
        if key == 'down': do_menu()
        if key == 'up': do_menu()
        scoreboard.set_mode_clock()
        scoreboard.update_clock()


if __name__ == "__main__":
    import sys
    try:
        sb_offline(sys.argv[1])
    except IndexError:
        sb_offline()