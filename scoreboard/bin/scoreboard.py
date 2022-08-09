#!/usr/bin/env python3

import sys
from time import sleep
import subprocess
from scoreboard import Config
from scoreboard.display_connection import Display
import signal

display = None
process = None
mode = None
running = True
mode_pin = 15


def switch_toggled(channel):
    global process
    global mode
    global mode_pin

    sleep(0.25)
    if process and ((GPIO.input(mode_pin) == 0 and mode == 'offline') or (GPIO.input(mode_pin) == 1 and mode == 'online')):
        print('Killing old process')
        process.kill()
        process = None


def sig_handler(signum, frame):
    global display
    global process
    global running

    running = False
    if process:
        display.send(['shutdown'])
        process.kill()
        process = None


def main():
    global display
    global process
    global mode
    global mode_pin
    global running

    if len(sys.argv) > 1:
        qt = True
        configfile = sys.argv[1]
    else:
        qt = False
        import RPi.GPIO as GPIO

    if qt:
        signal.signal(signal.SIGTERM, sig_handler)
        signal.signal(signal.SIGINT, sig_handler)
        display_process = subprocess.Popen(["display",configfile])
        config = Config(configfile)
        config.read()
    else:
        config = Config()
        config.read()
        mode_pin = config.scoreboard.getint("mode_pin", 15)

        # setup the online / offline switch
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(mode_pin, GPIO.IN, GPIO.PUD_UP)
        GPIO.add_event_detect(mode_pin, GPIO.BOTH, callback=switch_toggled, bouncetime=500)


    display = Display('localhost', config.display.getint("port", 6000))


    # start up the scoreboard in the correct mode
    while running:
        try:

            if qt:
                display.send(['mesg', 'Connecting ...'], 1, 8)
                print('Starting QT Mode')

                # start the app
                process = subprocess.Popen(["sb_online", configfile])
                process.wait()
                print('QT Mode Exited')

            elif GPIO.input(mode_pin) == 0:
                display.send(['mesg', 'Connecting ...'], 1, 20)
                print('Starting Online Mode')

                # online mode
                mode = 'online'
                sleep(0.25)

                # enable wifi
                with open('/etc/wpa_supplicant.conf', "w") as outfile:
                    subprocess.run(["wpa_passphrase", config.wifi["ssid"], config.wifi["password"]], stdout=outfile)
                    subprocess.run(["cat", "/etc/wpa_supplicant.base"], stdout=outfile)
                subprocess.run(["ifup", "wlan0"])
                subprocess.run(["wpa_cli", "reconfigure"])

                # start the bore local tunnel for remote login
                subprocess.run(["/etc/init.d/S55bore", "restart"])

                # check for software updates
                subprocess.run(["software_update"])

                # start the app
                process = subprocess.Popen(["sb_online"])
                process.wait()
                print('Online Mode Exited')

            else:
                display.send(['ping'], 1, 20)
                print('Starting Offline Mode')

                # offline mode
                mode = 'offline'
                process = subprocess.Popen(["sb_offline"])
                process.wait()
                print('Offline Mode Exited')

        except ConnectionRefusedError:
            sleep(0.25)
        except Exception as e:
            print(e)
