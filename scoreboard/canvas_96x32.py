
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image
from datetime import datetime

class Canvas:

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
        self.canvas = self.matrix.CreateFrameCanvas()

        self.rows = 32
        self.cols = 96
        self.load_logo(config.display["logo"])
        self.court = config.scoreboard["court"]

        # fonts
        self.court_font = graphics.Font()
        self.court_font.LoadFont("/usr/share/scoreboard/fonts/7x13B.bdf")
        self.time_font = graphics.Font()
        self.time_font.LoadFont("/usr/share/scoreboard/fonts/9x18B.bdf")
        self.player_name_font = graphics.Font()
        self.player_name_font.LoadFont("/usr/share/scoreboard/fonts/mono.bdf")
        self.score_font = graphics.Font()
        self.score_font.LoadFont("/usr/share/scoreboard/fonts/8x13B.bdf")
        self.mesg_font = graphics.Font()
        self.mesg_font.LoadFont("/usr/share/scoreboard/fonts/6x12.bdf")

        # colors
        self.court_color = graphics.Color(255, 0, 0)
        self.time_color = graphics.Color(255, 0, 0)
        self.player_name_color = graphics.Color(255, 191, 0)
        self.server_color = graphics.Color(0, 255, 0)
        self.score_color = graphics.Color(255, 0, 0)
        self.divide_line_color = graphics.Color(0, 0, 255)
        self.mesg_color = graphics.Color(255, 191, 0)


    def load_logo(self, org):
        try:
            self.logo = Image.open(f'/usr/share/scoreboard/{org}.png').convert('RGB')
        except:
            self.logo = Image.open('/usr/share/scoreboard/vbs.png').convert('RGB')


    def draw_player_name(self, name, max_length, x, y, server):
        if name == None: return
        name = name[0:max_length]
        color = self.player_name_color
        if server: color = self.server_color
        graphics.DrawText(self.canvas, self.player_name_font, x, y, color, name)


    def draw_score(self, score, x, y):
        graphics.DrawText(self.canvas, self.score_font, x, y, self.score_color, str(score).rjust(2))


    def update_clock(self):
        self.canvas.Clear()
        self.canvas.SetImage(self.logo)

        court_txt = f'COURT {self.court}'[0:9]
        courtx = 36 if len(court_txt) % 2 == 0 else 33
        graphics.DrawText(self.canvas, self.court_font, courtx, 13, self.court_color, court_txt.center(9))

        time = datetime.now().strftime("%-I:%M")
        timex = 46 if len(time) % 2 == 0 else 41
        graphics.DrawText(self.canvas, self.time_font, timex, 28, self.time_color, time)

        self.canvas = self.matrix.SwapOnVSync(self.canvas)



    def update_match(self, match):
        self.canvas.Clear()
        if match.player(1,3):
            self.draw_player_name(match.player(1, 1), 6, 1, 8, match.server() == 11)
            self.draw_player_name(match.player(1, 3), 6, 41, 8, match.server() == 13)
        else:
            self.draw_player_name(match.player(1, 1), 13, 1, 8, match.server() == 11)

        if match.player(1,4):
            self.draw_player_name(match.player(1, 2), 6, 1, 14, match.server() == 12)
            self.draw_player_name(match.player(1, 4), 6, 41, 14, match.server() == 14)
        else:
            self.draw_player_name(match.player(1, 2), 13, 1, 14, match.server() == 12)

        if match.player(2,3):
            self.draw_player_name(match.player(2, 1), 6, 1, 24, match.server() == 21)
            self.draw_player_name(match.player(2, 3), 6, 41, 24, match.server() == 23)
        else:
            self.draw_player_name(match.player(2, 1), 13, 1, 24, match.server() == 21)

        if match.player(2,4):
            self.draw_player_name(match.player(2, 2), 6, 1, 30, match.server() == 22)
            self.draw_player_name(match.player(2, 4), 6, 41, 30, match.server() == 24)
        else:
            self.draw_player_name(match.player(2, 2), 13, 1, 30, match.server() == 22)

        self.draw_score(match.team1_score(), 80, 12)
        self.draw_score(match.team2_score(), 80, 28)

        if match.team1_sets() > 0:
            graphics.DrawLine(self.canvas, 91, 13, 92, 13, self.server_color)
            graphics.DrawLine(self.canvas, 91, 14, 92, 14, self.server_color)

        if match.team1_sets() > 1:
            graphics.DrawLine(self.canvas, 86, 13, 87, 13, self.server_color)
            graphics.DrawLine(self.canvas, 86, 14, 87, 14, self.server_color)

        if match.team2_sets() > 0:
            graphics.DrawLine(self.canvas, 91, 29, 92, 29, self.server_color)
            graphics.DrawLine(self.canvas, 91, 30, 92, 30, self.server_color)

        if match.team2_sets() > 1:
            graphics.DrawLine(self.canvas, 86, 29, 87, 29, self.server_color)
            graphics.DrawLine(self.canvas, 86, 30, 87, 30, self.server_color)

        graphics.DrawLine(self.canvas, 0, 16, 95, 16, self.divide_line_color)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)


    def update_next_match(self, teams, countdown=-1):
        if int(countdown) > 0:
            next_match = f'NEXT: {int(countdown/60):2}:{(int(countdown)%60):02}'.center(16)
        else:
            next_match = "NEXT MATCH:"

        try:
            team1 = teams[0][0:16]
        except:
            team1 = 'TBD'
        try:
            team2 = teams[1][0:16]
        except:
            team2 = 'TBD'

        nextx = 0 if (len(next_match) % 2 == 0) else 3
        team1x = 0 if len(team1) % 2 == 0 else 3
        team2x = 0 if len(team2) % 2 == 0 else 3

        self.canvas.Clear()
        self.draw_player_name(next_match.center(16), 16, nextx, 7, True)
        self.draw_player_name(team1.center(16), 16, team1x, 15, False)
        self.draw_player_name("VS".center(16), 16, 0, 23, False)
        self.draw_player_name(team2.center(16), 16, team2x, 31, False)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)


    def show_message(self, msg):
        self.canvas.Clear()
        if len(msg) == 1:
            [x,l] = [1,16] if (len(msg[0]) % 2 == 0) else [3,15]
            graphics.DrawText(self.canvas, self.mesg_font, x, 18, self.mesg_color, msg[0].center(l))
        if len(msg) == 2:
            [x,l] = [1,16] if (len(msg[0]) % 2 == 0) else [3,15]
            graphics.DrawText(self.canvas, self.mesg_font, x, 14, self.mesg_color, msg[0].center(l))
            [x,l] = [1,16] if (len(msg[1]) % 2 == 0) else [3,15]
            graphics.DrawText(self.canvas, self.mesg_font, x, 24, self.mesg_color, msg[1].center(l))
        if len(msg) == 3:
            [x,l] = [1,16] if (len(msg[0]) % 2 == 0) else [3,15]
            graphics.DrawText(self.canvas, self.mesg_font, x, 10, self.mesg_color, msg[0].center(l))
            [x,l] = [1,16] if (len(msg[1]) % 2 == 0) else [3,15]
            graphics.DrawText(self.canvas, self.mesg_font, x, 20, self.mesg_color, msg[1].center(l))
            [x,l] = [1,16] if (len(msg[2]) % 2 == 0) else [3,15]
            graphics.DrawText(self.canvas, self.mesg_font, x, 30, self.mesg_color, msg[2].center(l))
        if len(msg) > 3:
            [x,l] = [1,16] if (len(msg[0]) % 2 == 0) else [3,15]
            graphics.DrawText(self.canvas, self.player_name_font, x, 7, self.mesg_color, msg[0].center(l))
            [x,l] = [1,16] if (len(msg[1]) % 2 == 0) else [3,15]
            graphics.DrawText(self.canvas, self.player_name_font, x, 15, self.mesg_color, msg[1].center(l))
            [x,l] = [1,16] if (len(msg[2]) % 2 == 0) else [3,15]
            graphics.DrawText(self.canvas, self.player_name_font, x, 23, self.mesg_color, msg[2].center(l))
            [x,l] = [1,16] if (len(msg[3]) % 2 == 0) else [3,15]
            graphics.DrawText(self.canvas, self.player_name_font, x, 31, self.mesg_color, msg[3].center(l))
        self.canvas = self.matrix.SwapOnVSync(self.canvas)


    def show_timer(self, msg, count):
        self.canvas.Clear()
        if msg:
            [x,l] = [1,16] if (len(msg) % 2 == 0) else [3,15]
            graphics.DrawText(self.canvas, self.mesg_font, x, 10, self.mesg_color, msg.center(l))

            msg2 = f'{int(count/60):2}:{(int(count)%60):02}'
            [x,l] = [8,9] if (len(msg2) % 2 == 0) else [3,10]
            graphics.DrawText(self.canvas, self.time_font, x, 28, self.score_color, msg2.center(l))
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
        else:
            msg2 = f'{int(count/60):2}:{(int(count)%60):02}'
            [x,l] = [8,9] if (len(msg2) % 2 == 0) else [3,10]
            graphics.DrawText(self.canvas, self.time_font, x, 20, self.score_color, msg2.center(l))
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
