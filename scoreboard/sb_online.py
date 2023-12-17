
from time import sleep
from websocket import WebSocketTimeoutException
import socket
import logging

from .scoreboard import Scoreboard
from .version import Version
from .api import Api


class AckTimeout(Exception):
    pass


scoreboard = Scoreboard()


def ping_success():
    global scoreboard
    scoreboard.set_connected()


def ping_timeout(ws_app, error):
    global scoreboard

    if isinstance(error, WebSocketTimeoutException):
        scoreboard.set_disconnected()
        scoreboard.api.logger.warning('Ping Timeout')



def sb_online(configfile=None):
    global scoreboard

    scoreboard.set_config(configfile)
    scoreboard.init_display_stack()
    scoreboard.init_gpio()
    scoreboard.init_solar_ctrl()

    scoreboard.api = Api(scoreboard.config.scoreboard["api_key"], scoreboard.config.scoreboard.getint('log_level', logging.WARNING), ping_timeout, ping_success)
    scoreboard.api.logger.info(f'Scoreboard {scoreboard.config.scoreboard["serial"]} Ver {Version.str()} Online')

    # log the current IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    scoreboard.api.logger.info(f'IP Address = {s.getsockname()[0]}')

    # check if the scoreboard has been reassigned to a different organization
    sb = scoreboard.api.scoreboard()
    logo_img = sb["organization"]["abbrev"]
    if logo_img != scoreboard.config.display.get("logo", logo_img):
        scoreboard.set_logo(logo_img)

    # check if the scoreboard has been reassigned to a different court
    court = str(sb['court'])
    if court != scoreboard.config.scoreboard["court"]:
        scoreboard.set_court(court)

    scoreboard.online()

    while True: sleep(1)
