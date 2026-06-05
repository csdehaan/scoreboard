#!/usr/bin/env python3

import sys
from time import sleep
import subprocess
from scoreboard import Config
from scoreboard.gpio import GPIO
from scoreboard.display_connection import Display
import signal

display = None
process = None
mode = None
running = True
mode_pin = 15
gpio = None


def switch_toggled(channel):
    global process
    global mode
    global gpio

    sleep(0.25)
    if process and ((gpio.online() and mode == 'offline') or (gpio.offline() and mode == 'online')):
        process.kill()
        process = None


def sig_handler(signum, frame):
    global process
    global running

    running = False
    if process:
        process.kill()
        process = None


def main():
    global display
    global process
    global mode
    global mode_pin
    global running
    global gpio

    if len(sys.argv) > 1:
        qt = True
        configfile = sys.argv[1]
    else:
        qt = False

    if qt:
        signal.signal(signal.SIGTERM, sig_handler)
        signal.signal(signal.SIGINT, sig_handler)
        subprocess.Popen(["display",configfile])
        config = Config(configfile)
        config.read()
        gpio = GPIO(config)
    else:
        config = Config()
        config.read()
        gpio = GPIO(config)

    # setup the online / offline switch
    gpio.set_online_switch_callback(switch_toggled)


    display = Display('127.0.0.1', config.display.getint("port", 6000))


    # start up the scoreboard in the correct mode
    while running:
        try:

            if qt:
                display.send(['splash', 'Connecting'], 1, 20)
                print('Starting QT Mode')

                # start the app
                process = subprocess.Popen(["sb_online", 'online', configfile])
                process.wait()
                print('QT Mode Exited')

            elif gpio.online():
                # turn off AP mode
                subprocess.run(["iwctl", "device", "wlan0", "set-property", "Mode", "station"])

                display.send(['splash', 'Connecting'], 1, 80)

                # online mode
                mode = 'online'
                sleep(0.25)

                # check for software updates
                subprocess.run(["software_update"])

                # start the app
                process = subprocess.Popen(["sb_online", mode])
                process.wait()

            else:
                # set wifi to AP mode
                subprocess.run(["iwctl", "device", "wlan0", "set-property", "Mode", "ap"])
                sleep(1)
                subprocess.run(["iwctl", "ap", "wlan0", "start", f'"{config.wifi.get("ssid")}"', f'"{config.wifi.get("password")}"'])

                display.send(['ping'], 1, 80)

                # offline mode
                mode = 'offline'
                process = subprocess.Popen(["sb_online", mode])
                process.wait()

        except ConnectionRefusedError:
            sleep(0.25)
        except Exception as e:
            print(e)
