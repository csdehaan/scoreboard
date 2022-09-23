
from time import sleep
try:
    import RPi.GPIO as RPI_GPIO
    rpi = True
except:
    rpi = False


class GPIO:
    def __init__(self, config):
        global rpi
        self.fan_fail_pin = config.scoreboard.getint("fan_fail_pin")
        self.fan_clear_pin = config.scoreboard.getint("fan_clear_pin")
        self.mode_pin = config.scoreboard.getint("mode_pin", 15)
        self.display_enable_pin = config.scoreboard.getint("display_enable_pin")
        if rpi:
            RPI_GPIO.setwarnings(False)
            RPI_GPIO.setmode(RPI_GPIO.BCM)
            if self.fan_fail_pin: RPI_GPIO.setup(self.fan_fail_pin, RPI_GPIO.IN, RPI_GPIO.PUD_UP)
            if self.fan_clear_pin:
                RPI_GPIO.setup(self.fan_clear_pin, RPI_GPIO.OUT)
                RPI_GPIO.output(self.fan_clear_pin, RPI_GPIO.LOW)
            RPI_GPIO.setup(self.mode_pin, RPI_GPIO.IN, RPI_GPIO.PUD_UP)
            if self.display_enable_pin: RPI_GPIO.setup(self.display_enable_pin, RPI_GPIO.OUT)


    def set_online_switch_callback(self, callback):
        global rpi
        if rpi:
            RPI_GPIO.add_event_detect(self.mode_pin, RPI_GPIO.BOTH, callback=callback, bouncetime=500)


    def online(self):
        global rpi
        if rpi:
            return RPI_GPIO.input(self.mode_pin) == 0
        return True


    def offline(self):
        global rpi
        if rpi:
            return RPI_GPIO.input(self.mode_pin) > 0
        return False


    def fan_alert(self):
        global rpi
        if rpi and self.fan_fail_pin:
            return RPI_GPIO.input(self.fan_fail_pin) == 0
        return False


    def fan_alert_clear(self):
        global rpi
        if rpi and self.fan_clear_pin:
            RPI_GPIO.output(self.fan_clear_pin, RPI_GPIO.HIGH)
            sleep(0.2)
            RPI_GPIO.output(self.fan_clear_pin, RPI_GPIO.LOW)


    def enable_display(self, enable=True):
        global rpi
        if rpi and self.display_enable_pin:
            if enable: RPI_GPIO.output(self.display_enable_pin, RPI_GPIO.LOW)
            else: RPI_GPIO.output(self.display_enable_pin, RPI_GPIO.HIGH)
