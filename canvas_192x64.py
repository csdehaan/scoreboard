
from rgbmatrix import graphics

class Canvas:

    def __init__(self, canvas):
        self.canvas = canvas

        # fonts
        self.court_font = graphics.Font()
        self.court_font.LoadFont("/usr/share/scoreboard/fonts/BVM-20.bdf")
        self.time_font = graphics.Font()
        self.time_font.LoadFont("/usr/share/scoreboard/fonts/BVM-25.bdf")
        self.player_name_font = graphics.Font()
        self.player_name_font.LoadFont("/usr/share/scoreboard/fonts/BVM-12.bdf")
        self.score_font = graphics.Font()
        self.score_font.LoadFont("/usr/share/scoreboard/fonts/BVM-20.bdf")
        self.mesg_font = graphics.Font()
        self.mesg_font.LoadFont("/usr/share/scoreboard/fonts/BVM-16.bdf")

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
        courtx = 72 if len(court_txt) % 2 == 0 else 66
        graphics.DrawText(self.canvas, self.court_font, courtx, 26, self.court_color, court_txt.center(9))

        timex = 92 if len(time) % 2 == 0 else 82
        graphics.DrawText(self.canvas, self.time_font, timex, 56, self.time_color, time)

        self.canvas = matrix.SwapOnVSync(self.canvas)



    def draw_match(self, matrix, match):
        self.canvas.Clear()
        self.draw_player_name(match.player(1, 1)[0:13], 4, 16, match.server() == 11)
        self.draw_player_name(match.player(1, 2)[0:13], 4, 28, match.server() == 12)
        self.draw_player_name(match.player(2, 1)[0:13], 4, 48, match.server() == 21)
        self.draw_player_name(match.player(2, 2)[0:13], 4, 60, match.server() == 22)
        self.draw_score(match.team1_score(), 158, 28)
        self.draw_score(match.team2_score(), 158, 58)
        graphics.DrawLine(self.canvas, 0, 32, 191, 32, self.divide_line_color)
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

        team1x = 0 if len(team1) % 2 == 0 else 6
        team2x = 0 if len(team2) % 2 == 0 else 6

        self.canvas.Clear()
        self.draw_player_name(next_match, 6, 14, True)
        self.draw_player_name(team1.center(16), team1x, 30, False)
        self.draw_player_name("VS".center(16), 0, 46, False)
        self.draw_player_name(team2.center(16), team2x, 62, False)
        self.canvas = matrix.SwapOnVSync(self.canvas)


    def draw_message(self, matrix, msg):
        self.canvas.Clear()
        if len(msg) == 1:
            graphics.DrawText(self.canvas, self.mesg_font, 2, 36, self.mesg_color, msg[0].center(16))
        if len(msg) == 2:
            graphics.DrawText(self.canvas, self.mesg_font, 2, 28, self.mesg_color, msg[0].center(16))
            graphics.DrawText(self.canvas, self.mesg_font, 2, 48, self.mesg_color, msg[1].center(16))
        if len(msg) == 3:
            graphics.DrawText(self.canvas, self.mesg_font, 2, 20, self.mesg_color, msg[0].center(16))
            graphics.DrawText(self.canvas, self.mesg_font, 2, 40, self.mesg_color, msg[1].center(16))
            graphics.DrawText(self.canvas, self.mesg_font, 2, 60, self.mesg_color, msg[2].center(16))
        self.canvas = matrix.SwapOnVSync(self.canvas)