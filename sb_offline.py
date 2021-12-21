#!/usr/bin/env python3

from config import Config
from controller import Controller
from match import Match

import threading
from multiprocessing.connection import Client


def update_clock():
    global display
    global controller

    if controller.status() == 'waiting':
        threading.Timer(10, update_clock).start()
        display.send(['clock'])


def update_score():
    global display
    global controller
    global match

    display.send(['match', match])
    controller.set_score(match.team1_score(), match.team2_score(), match.server())



def bt_button(value, options):
    global controller
    global match

    if value[0] == 49:
        match.team1_add_point()
        update_score()
    if value[0] == 50:
        match.reset()
        controller.set_status_scoring()
        update_score()
    if value[0] == 51:
        match.team2_add_point()
        update_score()
    if value[0] == 53:
        match.team1_subtract_point()
        update_score()
    if value[0] == 54:
        controller.set_status_waiting()
        update_clock()
    if value[0] == 55:
        match.team2_subtract_point()
        update_score()


config = Config()
config.read()

display = Client(('localhost', config.display.getint("port", 6000)), authkey=b'vbscores')

controller = Controller(f'SB {config.scoreboard["serial"]}', bt_button)
match = Match()

controller.set_status_waiting()
update_clock()
controller.publish()

