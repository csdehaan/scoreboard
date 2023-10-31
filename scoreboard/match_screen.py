
from PIL import Image, ImageDraw, ImageFont
from .periodic import periodic_task

class MatchScreen:
    def __init__(self, name, config):
        self.timer = None
        self.name = name
        self.visible = False
        self.cols = config.screen_cols()
        self.rows = config.screen_rows()
        self.resource_path = config.display.get("resource_path", "/usr/share/scoreboard")
        self.player_name_color = (255,191,0)
        self.server_color = (0,255,0)
        self.score_color = (255,0,0)
        self.divide_line_color = (0,0,255)
        self.set_dot_color = (0,255,0)
        if self.rows == 32:
            self.player_name_font = ImageFont.load(self.resource_path + '/fonts/mono.pil')
            self.score_font = ImageFont.load(self.resource_path + '/fonts/8x13B.pil')
            self.draw = self.draw32
        elif self.rows == 96:
            self.player_name_font = ImageFont.truetype('VeraMoBd.ttf', 22)
            self.score_font = ImageFont.truetype('VeraMono.ttf', 40)
            self.draw = self.draw96
        else:
            self.player_name_font = ImageFont.truetype('VeraMoBd.ttf', 14)
            self.score_font = ImageFont.truetype('VeraMono.ttf', 25)
            self.draw = self.draw64


    def clear(self):
        self.image = Image.new('RGB', (self.cols,self.rows))
        self.img_draw = ImageDraw.Draw(self.image)


    @periodic_task(1)
    def update(iteration, self, **kwargs):
        if kwargs['delay']-iteration <= 0:
            self.hide(display=kwargs.get('display'))


    def show(self, **kwargs):
        if kwargs.get('match'): self.draw(kwargs['match'])
        self.visible = True
        if kwargs.get('display'): kwargs['display'].update()


    def hide(self, **kwargs):
        if kwargs.get('delay'):
            if self.timer == None:
                self.timer = self.update(**kwargs)
        else:
            self.visible = False
            if self.timer:
                self.timer.set()
                self.timer = None
            if kwargs.get('display'): kwargs['display'].update()


    def draw_player_name(self, name, max_length, x, y, server):
        if name == None: return
        name = name[0:max_length]
        color = self.player_name_color
        if server: color = self.server_color
        self.img_draw.text((x,y), name, font=self.player_name_font, fill=color)


    def draw_score(self, score, x, y):
        self.img_draw.text((x,y), str(score).rjust(2), font=self.score_font, fill=self.score_color)


    def draw32(self, match):
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
            self.img_draw.pieslice([(91,13),(92,14)], start=0.0, end=360.0, fill=self.set_dot_color, outline=self.set_dot_color)

        if match.team1_sets() > 1:
            self.img_draw.pieslice([(86,13),(87,14)], start=0.0, end=360.0, fill=self.set_dot_color, outline=self.set_dot_color)

        if match.team2_sets() > 0:
            self.img_draw.pieslice([(91,29),(92,30)], start=0.0, end=360.0, fill=self.set_dot_color, outline=self.set_dot_color)

        if match.team2_sets() > 1:
            self.img_draw.pieslice([(86,29),(87,30)], start=0.0, end=360.0, fill=self.set_dot_color, outline=self.set_dot_color)

        self.img_draw.line([(0,16),(95,16)], fill=self.divide_line_color, width=1)


    def draw64(self, match):
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
            self.img_draw.pieslice([(181,25),(185,29)], start=0.0, end=360.0, fill=self.set_dot_color, outline=self.set_dot_color)

        if match.team1_sets() > 1:
            self.img_draw.pieslice([(171,25),(175,29)], start=0.0, end=360.0, fill=self.set_dot_color, outline=self.set_dot_color)

        if match.team2_sets() > 0:
            self.img_draw.pieslice([(181,57),(185,61)], start=0.0, end=360.0, fill=self.set_dot_color, outline=self.set_dot_color)

        if match.team2_sets() > 1:
            self.img_draw.pieslice([(171,57),(175,61)], start=0.0, end=360.0, fill=self.set_dot_color, outline=self.set_dot_color)

        self.img_draw.line([(0,32),(191,32)], fill=self.divide_line_color, width=1)


    def draw96(self, match):
        self.clear()

        if match.player(1,3):
            self.draw_player_name(match.player(1, 1), 8, 2, 0, match.server() == 11)
            self.draw_player_name(match.player(1, 3), 8, 105, 0, match.server() == 13)
        else:
            self.draw_player_name(match.player(1, 1), 16, 2, 0, match.server() == 11)

        if match.player(1,4):
            self.draw_player_name(match.player(1, 2), 8, 2, 24, match.server() == 12)
            self.draw_player_name(match.player(1, 4), 8, 105, 24, match.server() == 14)
        else:
            self.draw_player_name(match.player(1, 2), 16, 2, 24, match.server() == 12)

        if match.player(2,3):
            self.draw_player_name(match.player(2, 1), 8, 2, 48, match.server() == 21)
            self.draw_player_name(match.player(2, 3), 8, 105, 48, match.server() == 23)
        else:
            self.draw_player_name(match.player(2, 1), 16, 2, 48, match.server() == 21)

        if match.player(2,4):
            self.draw_player_name(match.player(2, 2), 8, 2, 72, match.server() == 22)
            self.draw_player_name(match.player(2, 4), 8, 105, 72, match.server() == 24)
        else:
            self.draw_player_name(match.player(2, 2), 16, 2, 72, match.server() == 22)

        self.draw_score(match.team1_score(), 208, -3)
        self.draw_score(match.team2_score(), 208, 46)

        if match.team1_sets() > 0:
            self.img_draw.pieslice([(245,40),(250,45)], start=0.0, end=360.0, fill=self.set_dot_color, outline=self.set_dot_color)

        if match.team1_sets() > 1:
            self.img_draw.pieslice([(233,40),(238,45)], start=0.0, end=360.0, fill=self.set_dot_color, outline=self.set_dot_color)

        if match.team2_sets() > 0:
            self.img_draw.pieslice([(245,88),(250,93)], start=0.0, end=360.0, fill=self.set_dot_color, outline=self.set_dot_color)

        if match.team2_sets() > 1:
            self.img_draw.pieslice([(233,88),(238,93)], start=0.0, end=360.0, fill=self.set_dot_color, outline=self.set_dot_color)

        self.img_draw.line([(0,48),(255,48)], fill=self.divide_line_color, width=1)
