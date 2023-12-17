
import subprocess
import re
import json
from time import sleep
from datetime import datetime
from pathlib import Path

from .config import Config
from .match import Match
from .display_connection import Display
from .clock_screen import ClockScreen
from .match_screen import MatchScreen
from .message_screen import MessageScreen
from .next_match_screen import NextMatchScreen
from .timer_screen import TimerScreen
from .periodic import periodic_task
from .workout import Workout
from .gpio import GPIO
from .renogy import Renogy


class Scoreboard:
    def __init__(self):
        self.config = None
        self.display = None
        self.connected = True
        self.screens = []
        self.api = None
        self.gpio = None
        self.solar_ctrl = None
        self.workout = None
        self.sides_switched = False


    def set_config(self, configfile):
        self.config = Config(configfile)
        self.config.read()


    def init_display_stack(self):
        self.open_display()
        self.add_screen(ClockScreen('clock', self.config))
        self.add_screen(MessageScreen('menu', self.config))
        self.add_screen(MessageScreen('workout', self.config))
        self.add_screen(TimerScreen('timer', self.config))
        self.add_screen(NextMatchScreen('next_match', self.config))
        self.add_screen(MatchScreen('match', self.config))
        self.add_screen(MessageScreen('switch_sides', self.config))
        self.add_screen(MessageScreen('timeout', self.config))
        self.add_screen(MessageScreen('connecting', self.config))

        self.find_screen('clock').run(self)
        self.find_screen('switch_sides').draw(['SWITCH','SIDES'])
        self.find_screen('connecting').draw(['Connecting ...'])


    def init_gpio(self):
        self.gpio = GPIO(self.config)


    def init_solar_ctrl(self):
        port = self.config.scoreboard.get("renogy_port")
        if port:
            baud = self.config.scoreboard.getint("renogy_baud", 9600)
            addr = self.config.scoreboard.getint("renogy_addr", 255)
            self.solar_ctrl = Renogy(port, baud, addr)


    ##############################################################
    ##  Display
    ##############################################################
    def open_display(self):
        self.display = Display('127.0.0.1', self.config.display.getint("port", 6000))


    def restart_display(self):
        self.display.send(['shutdown'])


    def set_brightness(self, brightness):
        brightness = int(brightness)
        if brightness > 200: brightness = 200
        if brightness < 0: brightness = 0
        extra_brightness = 0
        if brightness > 100:
            extra_brightness = brightness - 100
            brightness = 100
        pwm_lsb_nanoseconds = 300 + (extra_brightness * 10)
        pwm_bits = 8 - int(extra_brightness / 10)
        self.config.display['brightness'] = str(brightness)
        self.config.display['pwm_lsb_nanoseconds'] = str(pwm_lsb_nanoseconds)
        self.config.display['pwm_bits'] = str(pwm_bits)
        self.config.save()
        self.restart_display()


    ##############################################################
    ##  Manage Online Connection
    ##############################################################
    def online(self):
        self.api.logger.debug('Subscribing to score updates')
        self.api.subscribe_score_updates(self.rx_score_update)
        self.api.logger.debug('Subscribing to command queue')
        self.api.subscribe_command_queue(self.rx_command)
        self.status_timer = self.update_status()
        self.next_match_timer = self.update_next_match()


    def set_connected(self):
        self.connected = True
        self.find_screen('connecting').hide(display=self)


    def set_disconnected(self):
        self.connected = False
        self.find_screen('connecting').show(display=self)


    def is_connected(self):
        return self.connected


    def is_disconnected(self):
        return not self.connected


    ##############################################################
    ##  Manage Screens
    ##############################################################
    def add_screen(self, screen):
        self.screens.append(screen)


    def active_screen(self):
        for screen in reversed(self.screens):
            if screen.visible:
                return screen
        return None


    def find_screen(self, name):
        for screen in self.screens:
            if screen.name == name: return screen
        return None


    def clear_screen(self):
        for screen in self.screens:
            if screen.name == 'clock': screen.visible = True
            else: screen.visible = False
        self.update()


    def update(self):
        self.display.send(self.active_screen().image)


    ##############################################################
    ##  Clock Screen
    ##############################################################
    def set_logo(self, logo):
        self.config.display['logo'] = logo
        self.config.save()
        self.download_logo()
        self.find_screen('clock').load_logo(logo)


    def download_logo(self):
        filename = f'/media/data/logo/{self.config.display["logo"]}{self.config.screen_rows()}.png'
        if not Path(filename).is_file():
            # remount filesystem r/w
            if self.config.archive:
                subprocess.run(['mount','-o','remount,','rw','/dev/mmcblk0p2','/media/data'], capture_output=False)
            # download from web server
            self.api.get_scoreboard_logo(self.config.screen_rows(), filename)
            # remount filesystem r/o
            if self.config.archive:
                subprocess.run(['mount','-o','remount,','ro','/dev/mmcblk0p2','/media/data'], capture_output=False)


    def set_court(self, court):
        self.config.scoreboard['court'] = str(court)
        self.config.save()
        self.find_screen('clock').court = court


    ##############################################################
    ##  Scoring Screen
    ##############################################################
    def show_score(self, match):
        screen = self.find_screen('match')
        screen.show(match=match, display=self)


    def hide_score(self, delay=None):
        self.find_screen('match').hide(delay=delay, display=self)


    def show_switch_sides(self):
        self.find_screen('switch_sides').show(duration=10, display=self)


    def show_timeout(self, name, count=None):
        screen = self.find_screen('timeout')
        if name: screen.show(duration=count, mesg=[name, 'TIMEOUT', '{:01}:{:02}'.format(*divmod(count,60))], display=self, style='timeout')
        else: screen.hide(display=self)


    ##############################################################
    ##  Timer Screen
    ##############################################################
    def show_timer(self, message, time, autohide=None):
        self.find_screen('timer').show(mesg=message, duration=time, autohide=autohide, display=self)


    def hide_timer(self):
        self.find_screen('timer').hide(display=self)


    def pause_timer(self):
        self.find_screen('timer').pause()


    def reset_timer(self):
        self.find_screen('timer').reset()


    ##############################################################
    ##  Next Match Screen
    ##############################################################
    def show_next_match(self, team1, team2, ref, countdown=None):
        self.find_screen('next_match').show(team1=team1, team2=team2, ref=ref, countdown=countdown, display=self)


    def show_reservation(self, name, start, stop):
        self.find_screen('next_match').show(name=name, start=start, stop=stop, style='reservation', display=self)


    ##############################################################
    ##  Workout Screen
    ##############################################################
    def show_workout(self, workout):
        self.find_screen('workout').show(workout=workout, display=self)


    ##############################################################
    ##  Menu Screen
    ##############################################################
    def show_menu(self, menu):
        self.find_screen('menu').show(mesg=menu, display=self)


    def hide_menu(self):
        self.find_screen('menu').hide(display=self)


    ##############################################################
    ##  Subscription Callbacks
    ##############################################################
    def rx_score_update(self, message):
        self.api.logger.debug(f'rx_score_update: message={message}')

        try:
            m = json.loads(message)
            match = Match()
            match.from_json(m)
            if match.is_in_progress():
                self.show_score(match)
                if match.side_switch() and self.sides_switched == False:
                    self.sides_switched = True
                    sleep(1)
                    self.show_switch_sides()
                else:
                    self.sides_switched = False
            elif match.is_complete():
                self.show_score(match)
                self.hide_score(self.config.scoreboard.getint('end_match_delay', 60))

        except Exception as e:
            self.api.logger.error(f'Scoreboard#rx_score_update exception: {type(e).__name__} - {e}')


    def rx_command(self, message):
        self.api.logger.debug(f'rx_command: message={message}')

        try:
            m = json.loads(message)
            cmd = m.get('cmd')
            if cmd:
                rc = subprocess.run(cmd.split(' '), capture_output=True)
                self.api.logger.info(rc)
            cmd = m.get('start_timeout')
            if cmd:
                if cmd == 'MEDICAL': self.show_timeout(cmd, 300)
                else: self.show_timeout(cmd, 60)
            cmd = m.get('end_timeout')
            if cmd:
                self.show_timeout(None)
            cmd = m.get('start_timer')
            if cmd:
                time = int(cmd)
                if time == 0: self.hide_timer()
                else: self.show_timer(m.get('timer_msg'), time, 10)
            cmd = m.get('workout')
            if cmd:
                if (self.workout == None) or (self.workout and not self.workout.in_progress()):
                    self.workout = Workout(m.get('workout'))
                    self.workout.start()
                    self.show_workout(self.workout)
            cmd = m.get('ctrl_workout')
            if cmd and self.workout:
                if cmd == 'stop':
                    self.workout.stop()
                    self.workout = None
                if cmd == 'pause':
                    self.workout.pause()
                if cmd == 'step':
                    if self.workout.resting: self.workout.next_set()
                    else: self.workout.finish_set()
                if cmd == 'back':
                    self.workout.previous_set()
            cmd = m.get('brightness')
            if cmd:
                self.set_brightness(cmd)
            cmd = m.get('set_mode')
            if cmd:
                if cmd == 'clock':
                    self.clear_screen()

        except Exception as e:
            self.api.logger.error(f'rx_command exception: {type(e).__name__} - {e}')


    ##############################################################
    ##  Status
    ##############################################################
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


    @periodic_task(30)
    def update_status(iteration, self):
        status = {}
        try:
            temperature = self.cpu_temperature()
            status["cpu_temperature"] = temperature
            if temperature > 70:
                self.api.logger.warning(f'CPU Temperature = {temperature}')
        except:
            pass

        try:
            self.solar_ctrl.read()
            status["batt_charge"] = self.solar_ctrl.batt_soc
            status["load_watts"] = self.solar_ctrl.load_watts
            status["pv_watts"] = self.solar_ctrl.pv_watts
        except:
            pass

        try:
            status["fan_alert"] = self.gpio.fan_alert()
            if status["fan_alert"]:
                self.gpio.fan_alert_clear()
        except:
            pass

        try:
            status["wifi"] = self.wifi_signal()
        except:
            pass

        try:
            self.api.scoreboard_status(status)
        except:
            pass


    ##############################################################
    ##  Next Match Updates
    ##############################################################
    def get_next_match(self):
        self.api.logger.debug('get_next_match')
        try:
            next_match = self.api.next_match()
            # self.find_screen('connecting').visible = False
            if next_match:
                match = Match()
                match.from_json(next_match)
                return match

        except Exception as e:
            # self.set_disconnected()
            self.api.logger.exception(f'Scoreboard#get_next_match exception: {type(e).__name__} - {e}')

        return None


    def get_reservation(self):
        self.api.logger.debug('get_reservation')
        try:
            reservation = self.api.current_reservation()
            if reservation:
                reservation['start'] = datetime.fromisoformat(reservation['start'])
                reservation['stop'] = datetime.fromisoformat(reservation['stop'])
                return reservation

        except Exception as e:
            # self.set_disconnected()
            self.api.logger.exception(f'Scoreboard#get_reservation exception: {type(e).__name__} - {e}')

        return None


    @periodic_task(15)
    def update_next_match(iteration, self):
        try:
            next_match = self.get_next_match()
            self.api.logger.debug(f'update_next_match next match = {next_match}')
            if next_match:
                if next_match.is_scheduled():
                    self.show_next_match(next_match.team1(), next_match.team2(), next_match.referee())
                if next_match.is_in_progress():
                    self.show_score(next_match)
            else:
                reservation = self.get_reservation()
                self.api.logger.debug(f'update_next_match current reservation = {reservation}')
                if reservation:
                    self.show_reservation(reservation['name'], reservation['start'], reservation['stop'])
                else:
                    self.find_screen('next_match').hide(display=self)

        except Exception as e:
            self.api.logger.error(f'update_next_match exception: {type(e).__name__} - {e}')
