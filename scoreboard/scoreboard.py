
import subprocess
import re

from .config import Config
from .match import Match
from .display_connection import Display


class Scoreboard:
    def __init__(self):
        self.config = None
        self.display = None
        self.mode = 'clock'
        self.match = Match()
        self.connected = True


    def set_config(self, configfile):
        self.config = Config(configfile)
        self.config.read()


    def set_mode_clock(self):
        self.mode = 'clock'


    def set_mode_score(self):
        self.mode = 'score'


    def set_mode_menu(self):
        self.mode = 'menu'


    def set_mode_next_match(self):
        self.mode = 'next_match'


    def set_connected(self):
        self.connected = True


    def set_disconnected(self):
        self.connected = False


    def is_connected(self):
        return self.connected


    def is_disconnected(self):
        return not self.connected


    def open_display(self):
        self.display = Display('127.0.0.1', self.config.display.getint("port", 6000))


    def update_clock(self):
        if self.mode == 'clock': self.display.send(['clock'])


    def update_score(self):
        if self.mode == 'score': self.display.send(['match', self.match])


    def message(self, line1, line2=None, line3=None, line4=None):
        if line4 != None: self.display.send(['mesg', line1, line2, line3, line4])
        elif line3 != None: self.display.send(['mesg', line1, line2, line3])
        elif line2 != None: self.display.send(['mesg', line1, line2])
        else: self.display.send(['mesg', line1])


    def timer(self, message, time):
        self.display.send(['timer', message, time])


    def next_match(self, team1, team2, ref, countdown):
        self.display.send(['next_match', [team1, team2, ref], countdown])


    def set_court(self, court):
        self.config.scoreboard['court'] = str(court)
        self.config.save()
        self.display.send(['court', court])


    def set_brightness(self, brightness):
        brightness = int(brightness)
        if brightness > 200: brightness = 200
        if brightness < 0: brightness = 0
        extra_brightness = 0
        if brightness > 100:
            extra_brightness = brightness - 100
            brightness = 100
        pwm_lsb_nanoseconds = 300 + (extra_brightness * 10)
        pwm_bits = 11 - int(extra_brightness / 10)
        self.config.display['brightness'] = str(brightness)
        self.config.display['pwm_lsb_nanoseconds'] = str(pwm_lsb_nanoseconds)
        self.config.display['pwm_bits'] = str(pwm_bits)
        self.config.save()
        self.restart_display()


    def restart_display(self):
        self.display.send(['shutdown'])


    def cpu_temperature(self):
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as sensor:
            return int(sensor.readline()) / 1000.0


    def wifi_signal(self):
        wifi_sig = [3,6,8,10,13,15,17,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,51,53,55,56,58,60,61,63,64,66,67,69,70,71,73,74,75,76,78,79,80,81,82,83,84,85,86,87,88,89,90,90,91,92,93,93,94,95,95,96,96,97,97,98,98,98,99,99,99]
        rc = subprocess.run(['iwconfig'], capture_output=True)
        signal = int(re.search('Signal level=(-\d\d?) dBm', str(rc.stdout)).groups()[0])
        if signal > -21: return 100
        if signal < -92: return 1
        return wifi_sig[signal+20]
