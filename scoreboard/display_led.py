
from rgbmatrix import RGBMatrix, RGBMatrixOptions

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
        options.pwm_bits = config.display.getint("pwm_bits", 11)
        options.brightness = config.display.getint("brightness", 100)
        options.pwm_lsb_nanoseconds = config.display.getint("pwm_lsb_nanoseconds", 130)
        options.led_rgb_sequence = config.display.get("led_rgb_sequence", "RGB")
        options.gpio_slowdown = config.display.getint("gpio_slowdown", 1)
        options.limit_refresh_rate_hz = config.display.getint("limit_refresh", 0)
        self.matrix = RGBMatrix(options = options)
        self.frame_canvas = self.matrix.CreateFrameCanvas()

        if config.display.getint("cols") * config.display.getint("chain_length", 1) == 192:
            from scoreboard.canvas_192x64 import Canvas
        else:
            from scoreboard.canvas_96x32 import Canvas
        self.canvas = Canvas(config)


    def update(self):
        self.frame_canvas.Clear()
        self.frame_canvas.SetImage(self.canvas.image)
        self.frame_canvas = self.matrix.SwapOnVSync(self.frame_canvas)


    def update_clock(self):
        self.canvas.update_clock()
        self.update()



    def update_match(self, match):
        self.canvas.update_match(match)
        self.update()


    def update_next_match(self, teams, countdown=-1):
        self.canvas.update_next_match(teams, countdown)
        self.update()


    def show_message(self, msg):
        self.canvas.show_message(msg)
        self.update()


    def show_timer(self, msg, count):
        self.canvas.show_timer(msg, count)
        self.update()
