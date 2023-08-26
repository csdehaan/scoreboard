
from time import sleep
try:
    import RPi.GPIO as RPI_GPIO
    rpi = True
except:
    rpi = False

from threading import Lock
try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable
import os

_export_lock = Lock()
_open_pins = {}


GPIO_ROOT = '/sys/class/gpio'
GPIO_EXPORT = os.path.join(GPIO_ROOT, 'export')
GPIO_UNEXPORT = os.path.join(GPIO_ROOT, 'unexport')
FMODE = 'w'
IN, OUT = 'in', 'out'
LOW, HIGH = 0, 1

class GPIO:
    def __init__(self, config):
        global rpi
        self.fan_fail_gpio = None
        self.fan_clear_gpio = None
        self.fan_fail_pin = config.scoreboard.getint("fan_fail_pin")
        self.fan_clear_pin = config.scoreboard.getint("fan_clear_pin")
        self.mode_pin = config.scoreboard.getint("mode_pin", 15)
        self.display_enable_pin = config.scoreboard.getint("display_enable_pin")
        if rpi:
            RPI_GPIO.setwarnings(False)
            RPI_GPIO.setmode(RPI_GPIO.BCM)
            if self.fan_fail_pin:
                if self.fan_fail_pin > 400: self.fan_fail_gpio = GPIOPin(self.fan_fail_pin, IN)
                else: RPI_GPIO.setup(self.fan_fail_pin, RPI_GPIO.IN, RPI_GPIO.PUD_UP)
            if self.fan_clear_pin:
                if self.fan_clear_pin > 400:
                    self.fan_clear_gpio = GPIOPin(self.fan_clear_pin, OUT, LOW)
                else:
                    RPI_GPIO.setup(self.fan_clear_pin, RPI_GPIO.OUT)
                    RPI_GPIO.output(self.fan_clear_pin, RPI_GPIO.LOW)
            RPI_GPIO.setup(self.mode_pin, RPI_GPIO.IN, RPI_GPIO.PUD_UP)


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
        if rpi and self.fan_fail_pin and self.fan_fail_pin < 400:
            return RPI_GPIO.input(self.fan_fail_pin) == 0
        elif self.fan_fail_gpio:
            return self.fan_fail_gpio.read()
        return None


    def fan_alert_clear(self):
        global rpi
        if rpi and self.fan_clear_pin and self.fan_clear_pin < 400:
            RPI_GPIO.output(self.fan_clear_pin, RPI_GPIO.HIGH)
            sleep(0.2)
            RPI_GPIO.output(self.fan_clear_pin, RPI_GPIO.LOW)
        elif self.fan_clear_gpio:
            self.fan_clear_gpio.write(HIGH)
            sleep(0.2)
            self.fan_clear_gpio.write(LOW)


    def setup_display(self):
        global rpi
        if rpi and self.display_enable_pin:
            if self.display_enable_pin: RPI_GPIO.setup(self.display_enable_pin, RPI_GPIO.OUT)


    def enable_display(self, enable=True):
        global rpi
        if rpi and self.display_enable_pin:
            if enable: RPI_GPIO.output(self.display_enable_pin, RPI_GPIO.LOW)
            else: RPI_GPIO.output(self.display_enable_pin, RPI_GPIO.HIGH)




class GPIOPin(object):
    def __init__(self, pin, direction=None, initial=LOW):
        #  .configured() will raise a TypeError if "pin" is not convertable to int
        if GPIOPin.configured(pin, False) is not None:
            raise RuntimeError("pin {} is already configured".format(pin))

        self.value = None
        self.pin = int(pin)
        self.root = os.path.join(GPIO_ROOT, 'gpio{0}'.format(self.pin))

        if not os.path.exists(self.root):
            with _export_lock:
                with open(GPIO_EXPORT, FMODE) as f:
                    f.write(str(self.pin))
                    f.flush()

        # Using unbuffered binary IO is ~ 3x faster than text
        self.value = open(os.path.join(self.root, 'value'), 'wb+', buffering=0)

        # I hate manually calling .setup()!
        self.setup(direction, initial)

        # Add class to open pins
        _open_pins[self.pin] = self

    def setup(self, direction=None, initial=LOW):
        if direction is not None:
            self.set_direction(direction)

        if direction == OUT:
            self.write(initial)

    @staticmethod
    def configured(pin, assert_configured=True):
        try:
            # Implicitly convert str to int, ie: "1" -> 1
            pin = int(pin)
        except (TypeError, ValueError):
            raise ValueError("pin must be an int")

        if pin not in _open_pins and assert_configured:
            raise RuntimeError("pin {} is not configured".format(pin))

        return _open_pins.get(pin)

    def get_direction(self):
        with open(os.path.join(self.root, 'direction'), 'r') as f:
            return f.read().strip()

    def set_direction(self, mode):
        if mode not in (IN, OUT, LOW, HIGH):
            raise ValueError("Unsupported pin mode {}".format(mode))

        with open(os.path.join(self.root, 'direction'), FMODE) as f:
            f.write(str(mode))
            f.flush()

    def read(self):
        self.value.seek(0)
        value = self.value.read()
        try:
            # Python > 3 - bytes
            # Subtracting 48 converts an ASCII "0" or "1" to an int
            # ord("0") == 48
            return value[0] - 48
        except TypeError:
            # Python 2.x - str
            return int(value)

    def write(self, value):
        # write as bytes, about 3x faster than string IO
        self.value.write(b'1' if value else b'0')

    def cleanup(self):
        # Note: I have not put "cleanup" into the __del__ method since it's not
        # always desireable to unexport pins at program exit.
        # Additionally "open" can be deleted *before* the GPIOPin instance.
        self.value.close()

        if os.path.exists(self.root):
            with _export_lock:
                with open(GPIO_UNEXPORT, FMODE) as f:
                    f.write(str(self.pin))
                    f.flush()

        del _open_pins[self.pin]
