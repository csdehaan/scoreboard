
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

class Canvas:

    def __init__(self, config):

        self.rows = 64
        self.cols = 192
        self.resource_path = config.display.get("resource_path", "/usr/share/scoreboard")
        self.load_logo(config.display["logo"])
        self.court = config.scoreboard["court"]

        # fonts
        self.court_font = ImageFont.truetype('VeraMono.ttf', 20)
        self.time_font = ImageFont.truetype('VeraMono.ttf', 25)
        self.player_name_font = ImageFont.truetype('VeraMoBd.ttf', 14)
        self.score_font = ImageFont.truetype('VeraMono.ttf', 25)
        self.mesg_font = ImageFont.truetype('VeraMono.ttf', 16)

        # colors
        self.court_color = (255,0,0)
        self.time_color = (255,0,0)
        self.player_name_color = (255,191,0)
        self.server_color = (0,255,0)
        self.score_color = (255,0,0)
        self.divide_line_color = (0,0,255)
        self.mesg_color = (255,191,0)

        self.clear()


    def clear(self):
        self.image = Image.new('RGB', (self.cols,self.rows))
        self.draw = ImageDraw.Draw(self.image)


    def load_logo(self, org):
        try:
            self.logo = Image.open(f'{self.resource_path}/{org}64.png').convert('RGB')
        except:
            self.logo = Image.open(f'{self.resource_path}/vbs64.png').convert('RGB')


    def draw_player_name(self, name, max_length, x, y, server):
        if name == None: return
        name = name[0:max_length]
        color = self.player_name_color
        if server: color = self.server_color
        self.draw.text((x,y), name, font=self.player_name_font, fill=color)


    def draw_score(self, score, x, y):
        self.draw.text((x,y), str(score).rjust(2), font=self.score_font, fill=self.score_color)


    def update_clock(self):
        self.clear()
        self.image.paste(self.logo)

        court_txt = f'COURT {self.court}'[0:9]
        courtx = 69 if len(court_txt) % 2 == 0 else 75
        self.draw.text((courtx,7), court_txt.center(9), font=self.court_font, fill=self.court_color)

        time = datetime.now().strftime("%-I:%M")
        timex = 99 if len(time) % 2 == 0 else 92
        self.draw.text((timex,30), time, font=self.time_font, fill=self.time_color)



    def update_match(self, match):
        self.clear()

        if match.player(1,3):
            self.draw_player_name(match.player(1, 1), 10, 2, 0, match.server() == 11)
            self.draw_player_name(match.player(1, 3), 10, 80, 0, match.server() == 13)
        else:
            self.draw_player_name(match.player(1, 1), 20, 2, 0, match.server() == 11)

        if match.player(1,4):
            self.draw_player_name(match.player(1, 2), 10, 2, 16, match.server() == 12)
            self.draw_player_name(match.player(1, 4), 10, 80, 16, match.server() == 14)
        else:
            self.draw_player_name(match.player(1, 2), 20, 2, 16, match.server() == 12)

        if match.player(2,3):
            self.draw_player_name(match.player(2, 1), 10, 2, 32, match.server() == 21)
            self.draw_player_name(match.player(2, 3), 10, 80, 32, match.server() == 23)
        else:
            self.draw_player_name(match.player(2, 1), 20, 2, 32, match.server() == 21)

        if match.player(2,4):
            self.draw_player_name(match.player(2, 2), 10, 2, 48, match.server() == 22)
            self.draw_player_name(match.player(2, 4), 10, 80, 48, match.server() == 24)
        else:
            self.draw_player_name(match.player(2, 2), 20, 2, 48, match.server() == 22)

        self.draw_score(match.team1_score(), 160, -1)
        self.draw_score(match.team2_score(), 160, 31)

        if match.team1_sets() > 0:
            self.draw.pieslice([(181,25),(185,29)], start=0.0, end=360.0, fill=(0,255,0), outline=(0,255,0))

        if match.team1_sets() > 1:
            self.draw.pieslice([(171,25),(175,29)], start=0.0, end=360.0, fill=(0,255,0), outline=(0,255,0))

        if match.team2_sets() > 0:
            self.draw.pieslice([(181,57),(185,61)], start=0.0, end=360.0, fill=(0,255,0), outline=(0,255,0))

        if match.team2_sets() > 1:
            self.draw.pieslice([(171,57),(175,61)], start=0.0, end=360.0, fill=(0,255,0), outline=(0,255,0))

        self.draw.line([(0,32),(191,32)], fill=self.divide_line_color, width=1)


    def update_next_match(self, teams, countdown=-1):
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

        self.clear()
        self.draw_player_name(next_match.center(22), 22, nextx, -1, True)
        self.draw_player_name(team1.center(22), 22, team1x, 12, False)
        self.draw_player_name("VS".center(22), 22, 4, 24, False)
        self.draw_player_name(team2.center(22), 22, team2x, 36, False)
        self.draw_player_name(ref.center(22), 22, refx, 48, False)


    def show_message(self, msg):
        self.clear()
        if len(msg) == 1:
            [x,l] = [6,18] if (len(msg[0]) % 2 == 0) else [1,19]
            self.draw.text((x,22), msg[0].center(l), font=self.mesg_font, fill=self.mesg_color)
        if len(msg) == 2:
            [x,l] = [6,18] if (len(msg[0]) % 2 == 0) else [1,19]
            self.draw.text((x,10), msg[0].center(l), font=self.mesg_font, fill=self.mesg_color)
            [x,l] = [6,18] if (len(msg[1]) % 2 == 0) else [1,19]
            self.draw.text((x,32), msg[1].center(l), font=self.mesg_font, fill=self.mesg_color)
        if len(msg) == 3:
            [x,l] = [6,18] if (len(msg[0]) % 2 == 0) else [1,19]
            self.draw.text((x,3), msg[0].center(l), font=self.mesg_font, fill=self.mesg_color)
            [x,l] = [6,18] if (len(msg[1]) % 2 == 0) else [1,19]
            self.draw.text((x,23), msg[1].center(l), font=self.mesg_font, fill=self.mesg_color)
            [x,l] = [6,18] if (len(msg[2]) % 2 == 0) else [1,19]
            self.draw.text((x,43), msg[2].center(l), font=self.mesg_font, fill=self.mesg_color)
        if len(msg) > 3:
            [x,l] = [6,18] if (len(msg[0]) % 2 == 0) else [1,19]
            self.draw.text((x,0), msg[0].center(l), font=self.mesg_font, fill=self.mesg_color)
            [x,l] = [6,18] if (len(msg[1]) % 2 == 0) else [1,19]
            self.draw.text((x,15), msg[1].center(l), font=self.mesg_font, fill=self.mesg_color)
            [x,l] = [6,18] if (len(msg[2]) % 2 == 0) else [1,19]
            self.draw.text((x,30), msg[2].center(l), font=self.mesg_font, fill=self.mesg_color)
            [x,l] = [6,18] if (len(msg[3]) % 2 == 0) else [1,19]
            self.draw.text((x,45), msg[3].center(l), font=self.mesg_font, fill=self.mesg_color)


    def show_timer(self, msg, count):
        self.clear()
        if msg:
            [x,l] = [6,18] if (len(msg) % 2 == 0) else [1,19]
            self.draw.text((x,8), msg.center(l), font=self.mesg_font, fill=self.mesg_color)

            msg2 = f'{int(count/60):2}:{(int(count)%60):02}'
            [x,l] = [10,11] if (len(msg2) % 2 == 0) else [2,12]
            self.draw.text((x,30), msg2.center(l), font=self.time_font, fill=self.score_color)
        else:
            msg2 = f'{int(count/60):2}:{(int(count)%60):02}'
            [x,l] = [10,11] if (len(msg2) % 2 == 0) else [3,12]
            self.draw.text((x,18), msg2.center(l), font=self.time_font, fill=self.score_color)


    def show_splash(self, msg):
        self.clear()
        self.image.paste(self.logo)

        self.draw.text((75,5), "VB Scores", font=self.court_font, fill=self.mesg_color)
        mesgx = 60 if len(msg) % 2 == 0 else 64
        self.draw_player_name(msg.center(15), 15, mesgx, 38, True)
