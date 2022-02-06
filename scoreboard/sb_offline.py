
from scoreboard import Config, Match
from scoreboard.controller import Controller
from time import sleep

import threading
from multiprocessing.connection import Client

display = None
controller = None
match = None


def display_send(mesg, timeout=1):
    global display

    ack = None
    while ack != 'ack':
        try:
            display.send(mesg)
            if display.poll(timeout):
                ack = display.recv()
            else:
                raise EOFError
        except:
            display.close()
            display = Client(('localhost', 6000), authkey=b'vbscores')


def update_clock():
    global display
    global controller

    if controller.status() == 'waiting':
        threading.Timer(10, update_clock).start()
        display_send(['clock'])


def update_score():
    global display
    global controller
    global match

    display_send(['match', match])
    controller.set_score(match.team1_score(), match.team2_score(), match.server())



def bt_button(value, options):
    global controller
    global match

    if value[0] == 49:
        match.team1_add_point()
        update_score()
    if value[0] == 50:
        match.reset()
        controller.set_status_scoring(False)
        update_score()
    if value[0] == 51:
        match.team2_add_point()
        update_score()
    if value[0] == 53:
        match.team1_subtract_point()
        update_score()
    if value[0] == 54:
        controller.set_status_waiting(False)
        update_clock()
    if value[0] == 55:
        match.team2_subtract_point()
        update_score()
    if value[0] == 60:
        value.pop(0)
        name = bytes(value).decode('utf8')
        match.team1(name)
        controller.set_t1_name(name)
    if value[0] == 61:
        value.pop(0)
        name = bytes(value).decode('utf8')
        match.team2(name)
        controller.set_t2_name(name)


def sb_offline():
    global display
    global controller
    global match

    config = Config()
    config.read()

    while display == None:
        try:
            display = Client(('localhost', 6000), authkey=b'vbscores')
        except:
            sleep(0.25)

    controller = Controller(f'SB {config.scoreboard["serial"]}', bt_button)
    match = Match()

    controller.set_status_waiting(False)
    update_clock()
    controller.publish()
