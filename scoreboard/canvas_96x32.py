
from rgbmatrix import graphics

class Canvas:

    def __init__(self, canvas):
        self.canvas = canvas

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


    def draw_player_name(self, name, x, y, server):
        color = self.player_name_color
        if server: color = self.server_color
        graphics.DrawText(self.canvas, self.player_name_font, x, y, color, name)


    def draw_score(self, score, x, y):
        graphics.DrawText(self.canvas, self.score_font, x, y, self.score_color, str(score).rjust(2))


    def draw_clock(self, matrix, logo, court, time):
        self.canvas.Clear()
        self.canvas.SetImage(logo)

        court_txt = f'COURT {court}'[0:9]
        courtx = 36 if len(court_txt) % 2 == 0 else 33
        graphics.DrawText(self.canvas, self.court_font, courtx, 13, self.court_color, court_txt.center(9))

        timex = 46 if len(time) % 2 == 0 else 41
        graphics.DrawText(self.canvas, self.time_font, timex, 28, self.time_color, time)

        self.canvas = matrix.SwapOnVSync(self.canvas)



    def draw_match(self, matrix, match):
        self.canvas.Clear()
        if match.player(1,3):
            self.draw_player_name(match.player(1, 1)[0:6], 1, 8, match.server() == 11)
            self.draw_player_name(match.player(1, 3)[0:6], 41, 8, match.server() == 13)
        else:
            self.draw_player_name(match.player(1, 1)[0:13], 1, 8, match.server() == 11)

        if match.player(1,4):
            self.draw_player_name(match.player(1, 2)[0:6], 1, 14, match.server() == 12)
            self.draw_player_name(match.player(1, 4)[0:6], 41, 14, match.server() == 14)
        else:
            self.draw_player_name(match.player(1, 2)[0:13], 1, 14, match.server() == 12)

        if match.player(2,3):
            self.draw_player_name(match.player(2, 1)[0:6], 1, 24, match.server() == 21)
            self.draw_player_name(match.player(2, 3)[0:6], 41, 24, match.server() == 23)
        else:
            self.draw_player_name(match.player(2, 1)[0:13], 1, 24, match.server() == 21)

        if match.player(2,4):
            self.draw_player_name(match.player(2, 2)[0:6], 1, 30, match.server() == 22)
            self.draw_player_name(match.player(2, 4)[0:6], 41, 30, match.server() == 24)
        else:
            self.draw_player_name(match.player(2, 2)[0:13], 1, 30, match.server() == 22)

        self.draw_score(match.team1_score(), 80, 14)
        self.draw_score(match.team2_score(), 80, 29)

        graphics.DrawLine(self.canvas, 0, 16, 95, 16, self.divide_line_color)
        self.canvas = matrix.SwapOnVSync(self.canvas)


    def draw_next_match(self, matrix, teams, countdown=-1):
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
        self.canvas = matrix.SwapOnVSync(self.canvas)


    def draw_message(self, matrix, msg):
        self.canvas.Clear()
        if len(msg) == 1:
            graphics.DrawText(self.canvas, self.mesg_font, 1, 18, self.mesg_color, msg[0].center(16))
        if len(msg) == 2:
            graphics.DrawText(self.canvas, self.mesg_font, 1, 14, self.mesg_color, msg[0].center(16))
            graphics.DrawText(self.canvas, self.mesg_font, 1, 24, self.mesg_color, msg[1].center(16))
        if len(msg) == 3:
            graphics.DrawText(self.canvas, self.mesg_font, 1, 10, self.mesg_color, msg[0].center(16))
            graphics.DrawText(self.canvas, self.mesg_font, 1, 20, self.mesg_color, msg[1].center(16))
            graphics.DrawText(self.canvas, self.mesg_font, 1, 30, self.mesg_color, msg[2].center(16))
        self.canvas = matrix.SwapOnVSync(self.canvas)