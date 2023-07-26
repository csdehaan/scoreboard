
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from .gpio import GPIO
from .splash_screen import SplashScreen

class Display:

    def __init__(self, config):
        options = RGBMatrixOptions()
        options.drop_privileges = False
        options.rows = config.display.getint("rows")
        options.cols = config.display.getint("cols")
        options.chain_length = config.display.getint("chain_length", 1)
        options.parallel = config.display.getint("parallel", 1)
        options.row_address_type = config.display.getint("row_address_type", 0)
        options.multiplexing = config.display.getint("multiplexing", 0)
        options.pwm_bits = config.display.getint("pwm_bits", 8)
        options.brightness = config.display.getint("brightness", 100)
        options.pwm_lsb_nanoseconds = config.display.getint("pwm_lsb_nanoseconds", 300)
        options.led_rgb_sequence = config.display.get("led_rgb_sequence", "RGB")
        options.gpio_slowdown = config.display.getint("gpio_slowdown", 1)
        options.limit_refresh_rate_hz = config.display.getint("limit_refresh", 0)
        self.matrix = RGBMatrix(options = options)
        self.frame_canvas = self.matrix.CreateFrameCanvas()

        gpio = GPIO(config)
        gpio.setup_display()
        gpio.enable_display()

        self.splash = SplashScreen('splash', config)
        self.show_splash("Starting")


    def show(self, image):
        self.frame_canvas.Clear()
        self.frame_canvas.SetImage(image)
        self.frame_canvas = self.matrix.SwapOnVSync(self.frame_canvas)


    def show_splash(self, msg):
        self.splash.draw(msg)
        self.show(self.splash.image)
