
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
        self.score_font.LoadFont("/usr/share/scoreboard/fonts/BVM-25.bdf")
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


    def draw_player_name(self, name, max_length, x, y, server):
        if name == None: return
        name = name[0:max_length]
        color = self.player_name_color
        if server: color = self.server_color
        graphics.DrawText(self.canvas, self.player_name_font, x, y, color, name)


    def draw_score(self, score, x, y):
        graphics.DrawText(self.canvas, self.score_font, x, y, self.score_color, str(score).rjust(2))


    def draw_clock(self, matrix, logo, court, time):
        self.canvas.Clear()
        self.canvas.SetImage(logo)

        court_txt = f'COURT {court}'[0:9]
        courtx = 69 if len(court_txt) % 2 == 0 else 75
        graphics.DrawText(self.canvas, self.court_font, courtx, 25, self.court_color, court_txt.center(9))

        timex = 99 if len(time) % 2 == 0 else 92
        graphics.DrawText(self.canvas, self.time_font, timex, 53, self.time_color, time)

        self.canvas = matrix.SwapOnVSync(self.canvas)



    def draw_match(self, matrix, match):
        self.canvas.Clear()
        if match.player(1,3):
            self.draw_player_name(match.player(1, 1), 10, 2, 11, match.server() == 11)
            self.draw_player_name(match.player(1, 3), 10, 80, 11, match.server() == 13)
        else:
            self.draw_player_name(match.player(1, 1), 20, 2, 11, match.server() == 11)

        if match.player(1,4):
            self.draw_player_name(match.player(1, 2), 10, 2, 28, match.server() == 12)
            self.draw_player_name(match.player(1, 4), 10, 80, 28, match.server() == 14)
        else:
            self.draw_player_name(match.player(1, 2), 20, 2, 28, match.server() == 12)

        if match.player(2,3):
            self.draw_player_name(match.player(2, 1), 10, 2, 44, match.server() == 21)
            self.draw_player_name(match.player(2, 3), 10, 80, 44, match.server() == 23)
        else:
            self.draw_player_name(match.player(2, 1), 20, 2, 44, match.server() == 21)

        if match.player(2,4):
            self.draw_player_name(match.player(2, 2), 10, 2, 60, match.server() == 22)
            self.draw_player_name(match.player(2, 4), 10, 80, 60, match.server() == 24)
        else:
            self.draw_player_name(match.player(2, 2), 20, 2, 60, match.server() == 22)

        self.draw_score(match.team1_score(), 160, 23)
        self.draw_score(match.team2_score(), 160, 55)

        graphics.DrawCircle(self.canvas, 183, 28, 3, self.divide_line_color)
        graphics.DrawCircle(self.canvas, 172, 28, 3, self.divide_line_color)

        graphics.DrawCircle(self.canvas, 183, 60, 3, self.divide_line_color)
        graphics.DrawCircle(self.canvas, 172, 60, 3, self.divide_line_color)

        if match.team1_sets() > 0:
            graphics.DrawCircle(self.canvas, 172, 28, 3, self.server_color)
            graphics.DrawCircle(self.canvas, 172, 28, 2, self.server_color)
            graphics.DrawCircle(self.canvas, 172, 28, 1, self.server_color)

        if match.team1_sets() > 1:
            graphics.DrawCircle(self.canvas, 183, 28, 3, self.server_color)
            graphics.DrawCircle(self.canvas, 183, 28, 2, self.server_color)
            graphics.DrawCircle(self.canvas, 183, 28, 1, self.server_color)

        if match.team2_sets() > 0:
            graphics.DrawCircle(self.canvas, 172, 60, 3, self.server_color)
            graphics.DrawCircle(self.canvas, 172, 60, 2, self.server_color)
            graphics.DrawCircle(self.canvas, 172, 60, 1, self.server_color)

        if match.team2_sets() > 1:
            graphics.DrawCircle(self.canvas, 183, 60, 3, self.server_color)
            graphics.DrawCircle(self.canvas, 183, 60, 2, self.server_color)
            graphics.DrawCircle(self.canvas, 183, 60, 1, self.server_color)

        graphics.DrawLine(self.canvas, 0, 32, 191, 32, self.divide_line_color)
        self.canvas = matrix.SwapOnVSync(self.canvas)


    def draw_next_match(self, matrix, teams, countdown=-1):
        if int(countdown) > 0:
            next_match = f'NEXT: {int(countdown/60):2}:{(int(countdown)%60):02}'
        else:
            next_match = "NEXT MATCH:"

        try:
            team1 = teams[0][0:26]
        except:
            team1 = 'TBD'
        try:
            team2 = teams[1][0:26]
        except:
            team2 = 'TBD'
        try:
            ref = f'REF: {teams[2]}'[0:26]
        except:
            ref = 'REF: TBD'

        nextx = 4 if (len(next_match) % 2 == 0) else 8
        team1x = 4 if (len(team1) % 2 == 0) else 8
        team2x = 4 if (len(team2) % 2 == 0) else 8
        refx = 4 if (len(ref) % 2 == 0) else 8

        self.canvas.Clear()
        self.draw_player_name(next_match.center(26), 26, nextx, 10, True)
        self.draw_player_name(team1.center(26), 26, team1x, 23, False)
        self.draw_player_name("VS".center(26), 26, 4, 36, False)
        self.draw_player_name(team2.center(26), 26, team2x, 49, False)
        self.draw_player_name(ref.center(26), 26, refx, 62, False)
        self.canvas = matrix.SwapOnVSync(self.canvas)


    def draw_message(self, matrix, msg):
        self.canvas.Clear()
        if len(msg) == 1:
            [x,l] = [6,18] if (len(msg[0]) % 2 == 0) else [1,19]
            graphics.DrawText(self.canvas, self.mesg_font, x, 36, self.mesg_color, msg[0].center(l))
        if len(msg) == 2:
            [x,l] = [6,18] if (len(msg[0]) % 2 == 0) else [1,19]
            graphics.DrawText(self.canvas, self.mesg_font, x, 28, self.mesg_color, msg[0].center(l))
            [x,l] = [6,18] if (len(msg[1]) % 2 == 0) else [1,19]
            graphics.DrawText(self.canvas, self.mesg_font, x, 48, self.mesg_color, msg[1].center(l))
        if len(msg) == 3:
            [x,l] = [6,18] if (len(msg[0]) % 2 == 0) else [1,19]
            graphics.DrawText(self.canvas, self.mesg_font, x, 18, self.mesg_color, msg[0].center(l))
            [x,l] = [6,18] if (len(msg[1]) % 2 == 0) else [1,19]
            graphics.DrawText(self.canvas, self.mesg_font, x, 38, self.mesg_color, msg[1].center(l))
            [x,l] = [6,18] if (len(msg[2]) % 2 == 0) else [1,19]
            graphics.DrawText(self.canvas, self.mesg_font, x, 58, self.mesg_color, msg[2].center(l))
        if len(msg) > 3:
            [x,l] = [6,18] if (len(msg[0]) % 2 == 0) else [1,19]
            graphics.DrawText(self.canvas, self.mesg_font, x, 14, self.mesg_color, msg[0].center(l))
            [x,l] = [6,18] if (len(msg[1]) % 2 == 0) else [1,19]
            graphics.DrawText(self.canvas, self.mesg_font, x, 30, self.mesg_color, msg[1].center(l))
            [x,l] = [6,18] if (len(msg[2]) % 2 == 0) else [1,19]
            graphics.DrawText(self.canvas, self.mesg_font, x, 46, self.mesg_color, msg[2].center(l))
            [x,l] = [6,18] if (len(msg[3]) % 2 == 0) else [1,19]
            graphics.DrawText(self.canvas, self.mesg_font, x, 62, self.mesg_color, msg[3].center(l))
        self.canvas = matrix.SwapOnVSync(self.canvas)
