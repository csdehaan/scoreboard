
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

class Canvas:

    def __init__(self, config):

        self.rows = 32
        self.cols = 96
        self.resource_path = config.display.get("resource_path", "/usr/share/scoreboard")
        self.load_logo(config.display["logo"])
        self.court = config.scoreboard["court"]

        # fonts
        self.court_font = ImageFont.load(self.resource_path + '/fonts/7x13B.pil')
        self.time_font = ImageFont.load(self.resource_path + '/fonts/9x18B.pil')
        self.player_name_font = ImageFont.load(self.resource_path + '/fonts/mono.pil')
        self.score_font = ImageFont.load(self.resource_path + '/fonts/8x13B.pil')
        self.mesg_font = ImageFont.load(self.resource_path + '/fonts/6x12.pil')

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
            self.logo = Image.open(f'{self.resource_path}/{org}.png').convert('RGB')
        except:
            self.logo = Image.open(f'{self.resource_path}/vbs.png').convert('RGB')


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
        courtx = 36 if len(court_txt) % 2 == 0 else 33
        self.draw.text((courtx,2), court_txt.center(9), font=self.court_font, fill=self.court_color)

        time = datetime.now().strftime("%-I:%M")
        timex = 46 if len(time) % 2 == 0 else 41
        self.draw.text((timex,14), time, font=self.time_font, fill=self.time_color)



    def update_match(self, match):
        self.clear()

        if match.player(1,3):
            self.draw_player_name(match.player(1, 1), 6, 1, 3, match.server() == 11)
            self.draw_player_name(match.player(1, 3), 6, 41, 3, match.server() == 13)
        else:
            self.draw_player_name(match.player(1, 1), 13, 1, 3, match.server() == 11)

        if match.player(1,4):
            self.draw_player_name(match.player(1, 2), 6, 1, 9, match.server() == 12)
            self.draw_player_name(match.player(1, 4), 6, 41, 9, match.server() == 14)
        else:
            self.draw_player_name(match.player(1, 2), 13, 1, 9, match.server() == 12)

        if match.player(2,3):
            self.draw_player_name(match.player(2, 1), 6, 1, 19, match.server() == 21)
            self.draw_player_name(match.player(2, 3), 6, 41, 19, match.server() == 23)
        else:
            self.draw_player_name(match.player(2, 1), 13, 1, 19, match.server() == 21)

        if match.player(2,4):
            self.draw_player_name(match.player(2, 2), 6, 1, 25, match.server() == 22)
            self.draw_player_name(match.player(2, 4), 6, 41, 25, match.server() == 24)
        else:
            self.draw_player_name(match.player(2, 2), 13, 1, 25, match.server() == 22)

        self.draw_score(match.team1_score(), 80, 1)
        self.draw_score(match.team2_score(), 80, 17)

        if match.team1_sets() > 0:
            self.draw.pieslice([(91,13),(92,14)], start=0.0, end=360.0, fill=(0,255,0), outline=(0,255,0))

        if match.team1_sets() > 1:
            self.draw.pieslice([(86,13),(87,14)], start=0.0, end=360.0, fill=(0,255,0), outline=(0,255,0))

        if match.team2_sets() > 0:
            self.draw.pieslice([(91,29),(92,30)], start=0.0, end=360.0, fill=(0,255,0), outline=(0,255,0))

        if match.team2_sets() > 1:
            self.draw.pieslice([(86,29),(87,30)], start=0.0, end=360.0, fill=(0,255,0), outline=(0,255,0))

        self.draw.line([(0,16),(95,16)], fill=self.divide_line_color, width=1)


    def update_next_match(self, teams, countdown=-1):
        if int(countdown) > 0:
            next_match = f'NEXT: {int(countdown/60):2}:{(int(countdown)%60):02}'
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
        team1x = 0 if (len(team1) % 2 == 0) else 3
        team2x = 0 if (len(team2) % 2 == 0) else 3

        self.clear()
        self.draw_player_name(next_match.center(16), 16, nextx, 2, True)
        self.draw_player_name(team1.center(16), 16, team1x, 10, False)
        self.draw_player_name("VS".center(16), 16, 0, 18, False)
        self.draw_player_name(team2.center(16), 16, team2x, 26, False)


    def show_message(self, msg):
        self.clear()
        if len(msg) == 1:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [3,15]
            self.draw.text((x,10), text.center(l), font=self.mesg_font, fill=color)
        if len(msg) == 2:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [3,15]
            self.draw.text((x,5), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[1])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [3,15]
            self.draw.text((x,15), text.center(l), font=self.mesg_font, fill=color)
        if len(msg) == 3:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [3,15]
            self.draw.text((x,0), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[1])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [3,15]
            self.draw.text((x,10), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[2])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [3,15]
            self.draw.text((x,20), text.center(l), font=self.mesg_font, fill=color)
        if len(msg) > 3:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [4,15]
            self.draw.text((x,-3), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[1])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [4,15]
            self.draw.text((x,5), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[2])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [4,15]
            self.draw.text((x,13), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[3])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [4,15]
            self.draw.text((x,21), text.center(l), font=self.mesg_font, fill=color)


    def get_msg_text(self, msg):
            if isinstance(msg, (list,tuple)):
                return((msg[0],msg[1]))
            else:
                return((msg,self.mesg_color))


    def show_timer(self, msg, count):
        self.clear()
        if msg:
            [x,l] = [1,16] if (len(msg) % 2 == 0) else [3,15]
            self.draw.text((x,1), msg.center(l), font=self.mesg_font, fill=self.mesg_color)

            msg2 = f'{int(count/60):2}:{(int(count)%60):02}'
            [x,l] = [8,9] if (len(msg2) % 2 == 0) else [3,10]
            self.draw.text((x,12), msg2.center(l), font=self.time_font, fill=self.score_color)
        else:
            msg2 = f'{int(count/60):2}:{(int(count)%60):02}'
            [x,l] = [8,9] if (len(msg2) % 2 == 0) else [3,10]
            self.draw.text((x,8), msg2.center(l), font=self.time_font, fill=self.score_color)


    def show_splash(self, msg):
        self.clear()
        self.image.paste(self.logo)

        self.draw.text((38,2), "VB Scores", font=self.mesg_font, fill=self.mesg_color)
        mesgx = 29 if len(msg) % 2 == 0 else 32
        self.draw_player_name(msg.center(11), 11, mesgx, 22, True)
