
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

        self.rows = options.rows * options.parallel
        self.cols = options.cols * options.chain_length
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
        self.mesg_font = graphics.Font()
        self.mesg_font.LoadFont(config.display.get("mesg_font", "/usr/share/scoreboard/fonts/6x12.bdf"))

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
        [r,g,b] = config.display.get("mesg_color", "255,191,0").split(",")
        self.mesg_color = graphics.Color(int(r), int(g), int(b))

        # x,y coordinates
        self.player_x = int(self.cols * 0.020834)
        self.player1_y = int(self.rows * 0.25)
        self.player2_y = int(self.rows * 0.4375)
        self.player3_y = int(self.rows * 0.75)
        self.player4_y = int(self.rows * 0.9375)
        self.score_x = int(self.cols * 0.82292)
        self.score1_y = int(self.rows * 0.4375)
        self.score2_y = int(self.rows * 0.90625)


    def load_logo(self, org):
        size = '64' if self.rows == 64 else ''
        try:
            self.logo = Image.open(f'/usr/share/scoreboard/{org}{size}.png').convert('RGB')
        except:
            self.logo = Image.open(f'/usr/share/scoreboard/vbs{size}.png').convert('RGB')


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
        self.draw_player_name(match.player1()[0:13], self.player_x, self.player1_y, match.server() == 1)
        self.draw_player_name(match.player2()[0:13], self.player_x, self.player2_y, match.server() == 2)
        self.draw_player_name(match.player3()[0:13], self.player_x, self.player3_y, match.server() == 3)
        self.draw_player_name(match.player4()[0:13], self.player_x, self.player4_y, match.server() == 4)
        self.draw_score(match.team1_score(), self.score_x, self.score1_y)
        self.draw_score(match.team2_score(), self.score_x, self.score2_y)
        graphics.DrawLine(self.canvas, 0, self.rows / 2, self.cols, self.rows / 2, self.divide_line_color)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)


    def update_clock(self):
        self.canvas.Clear()
        self.draw_logo()

        court = f'COURT {self.court}'[0:9]
        courtx = int(self.cols * 0.375) if len(court) % 2 == 0 else int(self.cols * 0.3438)
        graphics.DrawText(self.canvas, self.court_font, courtx, int(self.rows * 0.40625), self.court_color, court.center(9))

        current_time = datetime.now().strftime("%-I:%M")
        timex = int(self.cols * 0.4792) if len(current_time) % 2 == 0 else int(self.cols * 0.4271)
        graphics.DrawText(self.canvas, self.time_font, timex, int(self.rows * 0.875), self.time_color, current_time)

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

        team1x = 0 if len(team1) % 2 == 0 else int(self.cols * 0.03125)
        team2x = 0 if len(team2) % 2 == 0 else int(self.cols * 0.03125)

        self.canvas.Clear()
        self.draw_player_name(next_match, int(self.cols * 0.03125), int(self.rows * 0.21875), True)
        self.draw_player_name(team1.center(16), team1x, int(self.rows * 0.46875), False)
        self.draw_player_name("VS".center(16), 0, int(self.rows * 0.71875), False)
        self.draw_player_name(team2.center(16), team2x, int(self.rows * 0.96875), False)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)


    def show_message(self, msg):
        self.canvas.Clear()
        if len(msg) == 1:
            graphics.DrawText(self.canvas, self.mesg_font, 1, int(self.rows * 0.5625), self.mesg_color, msg[0].center(16))
        if len(msg) == 2:
            graphics.DrawText(self.canvas, self.mesg_font, 1, int(self.rows * 0.4375), self.mesg_color, msg[0].center(16))
            graphics.DrawText(self.canvas, self.mesg_font, 1, int(self.rows * 0.75), self.mesg_color, msg[1].center(16))
        if len(msg) == 3:
            graphics.DrawText(self.canvas, self.mesg_font, 1, int(self.rows * 0.3125), self.mesg_color, msg[0].center(16))
            graphics.DrawText(self.canvas, self.mesg_font, 1, int(self.rows * 0.625), self.mesg_color, msg[1].center(16))
            graphics.DrawText(self.canvas, self.mesg_font, 1, int(self.rows * 0.9375), self.mesg_color, msg[2].center(16))
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

