
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image
from datetime import datetime
from multiprocessing.connection import Listener

from config import Config
from match import Match

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

        self.load_logo(config.display["logo"])
        self.court = config.scoreboard["court"]
        self.matrix = RGBMatrix(options = options)
        self.canvas = self.matrix.CreateFrameCanvas()

        # fonts
        self.court_font = graphics.Font()
        self.court_font.LoadFont(config.display["court_font"])
        self.time_font = graphics.Font()
        self.time_font.LoadFont(config.display["time_font"])
        self.player_name_font = graphics.Font()
        self.player_name_font.LoadFont(config.display["player_name_font"])
        self.score_font = graphics.Font()
        self.score_font.LoadFont(config.display["score_font"])

        # colors
        [r,g,b] = config.display["court_color"].split(",")
        self.court_color = graphics.Color(int(r), int(g), int(b))
        [r,g,b] = config.display["time_color"].split(",")
        self.time_color = graphics.Color(int(r), int(g), int(b))
        [r,g,b] = config.display["player_name_color"].split(",")
        self.player_name_color = graphics.Color(int(r), int(g), int(b))
        [r,g,b] = config.display["server_color"].split(",")
        self.server_color = graphics.Color(int(r), int(g), int(b))
        [r,g,b] = config.display["score_color"].split(",")
        self.score_color = graphics.Color(int(r), int(g), int(b))
        [r,g,b] = config.display["divide_line_color"].split(",")
        self.divide_line_color = graphics.Color(int(r), int(g), int(b))


    def load_logo(self, file):
        try:
            self.logo = Image.open(f'/usr/share/scoreboard/{file}').convert('RGB')
        except:
            self.logo = Image.open("/usr/share/scoreboard/vbs.png").convert('RGB')


    def draw_player_name(self, name, x, y, server):
        color = self.player_name_color
        if server: color = self.server_color
        graphics.DrawText(self.canvas, self.player_name_font, x, y, color, name)


    def draw_score(self, score, x, y):
        graphics.DrawText(self.canvas, self.score_font, x, y, self.score_color, str(score).rjust(2))


    def draw_logo(self):
        self.canvas.SetImage(self.logo)


    def update_match(self, match):
        self.canvas.Clear()
        self.draw_player_name(match.player1()[0:13], 2, 8, match.server() == 1)
        self.draw_player_name(match.player2()[0:13], 2, 14, match.server() == 2)
        self.draw_player_name(match.player3()[0:13], 2, 24, match.server() == 3)
        self.draw_player_name(match.player4()[0:13], 2, 30, match.server() == 4)
        self.draw_score(match.team1_score(), 79, 14)
        self.draw_score(match.team2_score(), 79, 29)
        graphics.DrawLine(self.canvas, 0, 16, 95, 16, self.divide_line_color)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)


    def update_clock(self):
        self.canvas.Clear()
        self.draw_logo()

        court = f'COURT {self.court}'[0:9]
        courtx = 36 if len(court) % 2 == 0 else 33
        graphics.DrawText(self.canvas, self.court_font, courtx, 13, self.court_color, court.center(9))

        current_time = datetime.now().strftime("%-I:%M")
        timex = 46 if len(current_time) % 2 == 0 else 41
        graphics.DrawText(self.canvas, self.time_font, timex, 28, self.time_color, current_time)

        self.canvas = self.matrix.SwapOnVSync(self.canvas)


    def update_next_match(self, teams, countdown=-1):
        if int(countdown) > 0:
            next_match = f'NEXT: {int(countdown/60):2}:{(int(countdown)%60):02}'.center(16)
        else:
            next_match = "NEXT MATCH:".center(16)

        try:
            team1 = teams[0][0:16]
        except:
            team1 = 'TBD'
        try:
            team2 = teams[1][0:16]
        except:
            team2 = 'TBD'

        team1x = 0 if len(team1) % 2 == 0 else 3
        team2x = 0 if len(team2) % 2 == 0 else 3

        self.canvas.Clear()
        self.draw_player_name(next_match, 3, 7, True)
        self.draw_player_name(team1.center(16), team1x, 15, False)
        self.draw_player_name("VS".center(16), 0, 23, False)
        self.draw_player_name(team2.center(16), team2x, 31, False)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)


    def show_message(self, msg):
        self.canvas.Clear()
        if len(msg) == 1:
            graphics.DrawText(self.canvas, self.score_font, 1, 18, msg[0].center(16))
        if len(msg) == 2:
            graphics.DrawText(self.canvas, self.score_font, 1, 14, msg[0].center(16))
            graphics.DrawText(self.canvas, self.score_font, 1, 24, msg[1].center(16))
        if len(msg) == 3:
            graphics.DrawText(self.canvas, self.score_font, 1, 10, msg[0].center(16))
            graphics.DrawText(self.canvas, self.score_font, 1, 20, msg[1].center(16))
            graphics.DrawText(self.canvas, self.score_font, 1, 30, msg[2].center(16))
        self.canvas = self.matrix.SwapOnVSync(self.canvas)



config = Config()
config.read()

display = Display(config)

listener = Listener(('localhost', config.display.getint("port", 6000)), authkey=b'vbscores')
running = True
while running:
    conn = listener.accept()

    try:
        while True:
            msg = conn.recv()
            if msg[0] == 'clock':
                display.update_clock()
            if msg[0] == 'match':
                display.update_match(msg[1])
            if msg[0] == 'next_match':
                display.update_next_match(msg[1], msg[2])
            if msg[0] == 'court':
                display.court = msg[1]
            if msg[0] == 'logo':
                display.load_logo(msg[1])
            if msg[0] == 'mesg':
                display.show_message(msg[1:4])
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

