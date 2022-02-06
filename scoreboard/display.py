
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
from datetime import datetime
from multiprocessing.connection import Listener

from scoreboard import Config

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

        self.rows = options.rows * options.parallel
        self.cols = options.cols * options.chain_length
        self.load_logo(config.display["logo"])
        self.court = config.scoreboard["court"]
        self.matrix = RGBMatrix(options = options)

        if self.cols == 192:
            from scoreboard.canvas_192x64 import Canvas
        else:
            from scoreboard.canvas_96x32 import Canvas
        self.canvas = Canvas(self.matrix.CreateFrameCanvas())


    def load_logo(self, org):
        size = '64' if self.rows == 64 else ''
        try:
            self.logo = Image.open(f'/usr/share/scoreboard/{org}{size}.png').convert('RGB')
        except:
            self.logo = Image.open(f'/usr/share/scoreboard/vbs{size}.png').convert('RGB')


    def update_match(self, match):
        self.canvas.draw_match(self.matrix, match)


    def update_clock(self):
        self.canvas.draw_clock(self.matrix, self.logo, self.court, datetime.now().strftime("%-I:%M"))


    def update_next_match(self, teams, countdown=-1):
        self.canvas.draw_next_match(self.matrix, teams, countdown)


    def show_message(self, msg):
        self.canvas.draw_message(self.matrix, msg)



def rgb_display():
    config = Config()
    config.read()

    display = Display(config)

    listener = Listener(('0.0.0.0', 6000), authkey=b'vbscores')
    running = True
    while running:
        conn = listener.accept()

        try:
            while True:
                msg = conn.recv()
                if msg[0] == 'clock':
                    display.update_clock()
                    display.send('ack')
                if msg[0] == 'match':
                    display.update_match(msg[1])
                    display.send('ack')
                if msg[0] == 'next_match':
                    display.update_next_match(msg[1], msg[2])
                    display.send('ack')
                if msg[0] == 'court':
                    display.court = msg[1]
                    display.send('ack')
                if msg[0] == 'logo':
                    display.load_logo(msg[1])
                    display.send('ack')
                if msg[0] == 'mesg':
                    display.show_message(msg[1:5])
                    display.send('ack')
                if msg[0] == 'close':
                    conn.close()
                    break
                if msg[0] == 'shutdown':
                    conn.close()
                    running = False
                    break
        except Exception as e:
            print(e)

    listener.close()
