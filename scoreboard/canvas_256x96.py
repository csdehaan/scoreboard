
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

class Canvas:

    def __init__(self, config):

        self.rows = 96
        self.cols = 256
        self.resource_path = config.display.get("resource_path", "/usr/share/scoreboard")
        self.load_logo(config.display["logo"])
        self.court = config.scoreboard["court"]

        # fonts
        self.court_font = ImageFont.truetype('VeraMono.ttf', 28)
        self.time_font = ImageFont.truetype('VeraMono.ttf', 30)
        self.player_name_font = ImageFont.truetype('VeraMoBd.ttf', 18)
        self.score_font = ImageFont.truetype('VeraMono.ttf', 40)
        self.mesg_font = ImageFont.truetype('VeraMono.ttf', 21)

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
            self.logo = Image.open(f'{self.resource_path}/{org}96.png').convert('RGB')
        except:
            self.logo = Image.open(f'{self.resource_path}/vbs96.png').convert('RGB')


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
        courtx = 92 if len(court_txt) % 2 == 0 else 100
        self.draw.text((courtx,10), court_txt.center(9), font=self.court_font, fill=self.court_color)

        time = datetime.now().strftime("%-I:%M")
        timex = 140 if len(time) % 2 == 0 else 131
        self.draw.text((timex,48), time, font=self.time_font, fill=self.time_color)



    def update_match(self, match):
        self.clear()

        if match.player(1,3):
            self.draw_player_name(match.player(1, 1), 10, 2, 0, match.server() == 11)
            self.draw_player_name(match.player(1, 3), 10, 105, 0, match.server() == 13)
        else:
            self.draw_player_name(match.player(1, 1), 20, 2, 0, match.server() == 11)

        if match.player(1,4):
            self.draw_player_name(match.player(1, 2), 10, 2, 24, match.server() == 12)
            self.draw_player_name(match.player(1, 4), 10, 105, 24, match.server() == 14)
        else:
            self.draw_player_name(match.player(1, 2), 20, 2, 24, match.server() == 12)

        if match.player(2,3):
            self.draw_player_name(match.player(2, 1), 10, 2, 48, match.server() == 21)
            self.draw_player_name(match.player(2, 3), 10, 105, 48, match.server() == 23)
        else:
            self.draw_player_name(match.player(2, 1), 20, 2, 48, match.server() == 21)

        if match.player(2,4):
            self.draw_player_name(match.player(2, 2), 10, 2, 72, match.server() == 22)
            self.draw_player_name(match.player(2, 4), 10, 105, 72, match.server() == 24)
        else:
            self.draw_player_name(match.player(2, 2), 20, 2, 72, match.server() == 22)

        self.draw_score(match.team1_score(), 208, -3)
        self.draw_score(match.team2_score(), 208, 46)

        if match.team1_sets() > 0:
            self.draw.pieslice([(245,40),(250,45)], start=0.0, end=360.0, fill=(0,255,0), outline=(0,255,0))

        if match.team1_sets() > 1:
            self.draw.pieslice([(233,40),(238,45)], start=0.0, end=360.0, fill=(0,255,0), outline=(0,255,0))

        if match.team2_sets() > 0:
            self.draw.pieslice([(245,88),(250,93)], start=0.0, end=360.0, fill=(0,255,0), outline=(0,255,0))

        if match.team2_sets() > 1:
            self.draw.pieslice([(233,88),(238,93)], start=0.0, end=360.0, fill=(0,255,0), outline=(0,255,0))

        self.draw.line([(0,48),(255,48)], fill=self.divide_line_color, width=1)


    def update_next_match(self, teams, countdown=-1):
        if int(countdown) > 0:
            next_match = f'NEXT: {int(countdown/60):2}:{(int(countdown)%60):02}'
        else:
            next_match = "NEXT MATCH:"

        try:
            team1 = teams[0][0:22]
        except:
            team1 = 'TBD'
        try:
            team2 = teams[1][0:22]
        except:
            team2 = 'TBD'
        try:
            ref = f'REF: {teams[2]}'[0:22]
        except:
            ref = 'REF: TBD'

        nextx = 8 if (len(next_match) % 2 == 0) else 14
        team1x = 8 if (len(team1) % 2 == 0) else 14
        team2x = 8 if (len(team2) % 2 == 0) else 14
        refx = 8 if (len(ref) % 2 == 0) else 14

        self.clear()
        self.draw_player_name(next_match.center(22), 22, nextx, -1, True)
        self.draw_player_name(team1.center(22), 22, team1x, 19, False)
        self.draw_player_name("VS".center(22), 22, 8, 38, False)
        self.draw_player_name(team2.center(22), 22, team2x, 57, False)
        self.draw_player_name(ref.center(22), 22, refx, 76, False)


    def show_message(self, msg):
        self.clear()
        if len(msg) == 1:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.draw.text((x,34), text.center(l), font=self.mesg_font, fill=color)
        if len(msg) == 2:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.draw.text((x,15), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[1])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.draw.text((x,48), text.center(l), font=self.mesg_font, fill=color)
        if len(msg) == 3:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.draw.text((x,4), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[1])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.draw.text((x,35), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[2])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.draw.text((x,66), text.center(l), font=self.mesg_font, fill=color)
        if len(msg) > 3:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.draw.text((x,1), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[1])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.draw.text((x,24), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[2])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.draw.text((x,47), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[3])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.draw.text((x,70), text.center(l), font=self.mesg_font, fill=color)


    def get_msg_text(self, msg):
            if isinstance(msg, (list,tuple)):
                return((msg[0][0:20],msg[1]))
            else:
                return((msg[0:20],self.mesg_color))


    def show_timer(self, msg, count):
        self.clear()
        if msg:
            msg = msg[0:20]
            [x,l] = [1,20] if (len(msg) % 2 == 0) else [7,19]
            self.draw.text((x,10), msg.center(l), font=self.mesg_font, fill=self.mesg_color)

            msg2 = f'{int(count/60):2}:{(int(count)%60):02}'
            [x,l] = [15,12] if (len(msg2) % 2 == 0) else [10,13]
            self.draw.text((x,45), msg2.center(l), font=self.time_font, fill=self.score_color)
        else:
            msg2 = f'{int(count/60):2}:{(int(count)%60):02}'
            [x,l] = [15,12] if (len(msg2) % 2 == 0) else [10,13]
            self.draw.text((x,30), msg2.center(l), font=self.time_font, fill=self.score_color)


    def show_splash(self, msg):
        self.clear()
        self.image.paste(self.logo)

        self.draw.text((101,15), "VB Scores", font=self.court_font, fill=self.mesg_color)
        mesgx = 89 if len(msg) % 2 == 0 else 95
        self.draw_player_name(msg.center(15), 15, mesgx, 55, True)
