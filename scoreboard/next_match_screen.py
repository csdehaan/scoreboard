
from PIL import Image, ImageDraw, ImageFont
from .periodic import periodic_task

class NextMatchScreen:
    def __init__(self, name, config):
        self.timer = None
        self.name = name
        self.visible = False
        self.cols = config.screen_cols()
        self.rows = config.screen_rows()
        self.resource_path = config.display.get("resource_path", "/usr/share/scoreboard")
        self.team_color = (255,191,0)
        self.next_match_color = (0,255,0)
        self.team1 = 'TBD'
        self.team2 = 'TBD'
        self.ref = 'TBD'
        self.countdown = -1
        if self.rows == 32:
            self.text_font = ImageFont.load(self.resource_path + '/fonts/mono.pil')
            self.draw = self.draw32
        elif self.rows == 96:
            self.text_font = ImageFont.truetype('VeraMoBd.ttf', 18)
            self.draw = self.draw96
        else:
            self.text_font = ImageFont.truetype('VeraMoBd.ttf', 14)
            self.draw = self.draw64


    def clear(self):
        self.image = Image.new('RGB', (self.cols,self.rows))
        self.img_draw = ImageDraw.Draw(self.image)


    @periodic_task(1)
    def update(iteration, self, **kwargs):
        self.countdown = kwargs['countdown']-iteration
        if self.countdown <= 0:
            self.timer.set()
            self.timer = None
        self.draw()
        if kwargs.get('display'): kwargs['display'].update()


    def show(self, **kwargs):
        self.team1 = kwargs['team1']
        self.team2 = kwargs['team2']
        self.ref = kwargs['ref']
        self.visible = True
        if kwargs.get('countdown') and self.timer == None:
            self.timer = self.update(**kwargs)
        else:
            self.draw()
            if kwargs.get('display'): kwargs['display'].update()


    def hide(self, **kwargs):
        self.visible = False
        self.countdown = -1
        if self.timer:
            self.timer.set()
            self.timer = None
        if kwargs.get('display'): kwargs['display'].update()


    def draw_text_line(self, text, max_length, x, y, color):
        if text == None: return
        text = text[0:max_length]
        self.img_draw.text((x,y), text, font=self.text_font, fill=color)


    def draw32(self):
        if self.countdown > 0:
            next_match = f'NEXT: {int(self.countdown/60):2}:{(self.countdown%60):02}'
        else:
            next_match = "NEXT MATCH:"

        try:
            team1 = self.team1[0:16]
        except:
            team1 = 'TBD'
        try:
            team2 = self.team2[0:16]
        except:
            team2 = 'TBD'

        nextx = 0 if (len(next_match) % 2 == 0) else 3
        team1x = 0 if (len(team1) % 2 == 0) else 3
        team2x = 0 if (len(team2) % 2 == 0) else 3

        self.clear()
        self.draw_text_line(next_match.center(16), 16, nextx, 2, self.next_match_color)
        self.draw_text_line(team1.center(16), 16, team1x, 10, self.team_color)
        self.draw_text_line("VS".center(16), 16, 0, 18, self.team_color)
        self.draw_text_line(team2.center(16), 16, team2x, 26, self.team_color)


    def draw64(self):
        if self.countdown > 0:
            next_match = f'NEXT: {int(self.countdown/60):2}:{(self.countdown%60):02}'
        else:
            next_match = "NEXT MATCH:"

        try:
            team1 = self.team1[0:26]
        except:
            team1 = 'TBD'
        try:
            team2 = self.team2[0:26]
        except:
            team2 = 'TBD'
        try:
            ref = f'REF: {self.ref}'[0:26]
        except:
            ref = 'REF: TBD'

        nextx = 4 if (len(next_match) % 2 == 0) else 8
        team1x = 4 if (len(team1) % 2 == 0) else 8
        team2x = 4 if (len(team2) % 2 == 0) else 8
        refx = 4 if (len(ref) % 2 == 0) else 8

        self.clear()
        self.draw_text_line(next_match.center(22), 22, nextx, -1, self.next_match_color)
        self.draw_text_line(team1.center(22), 22, team1x, 12, self.team_color)
        self.draw_text_line("VS".center(22), 22, 4, 24, self.team_color)
        self.draw_text_line(team2.center(22), 22, team2x, 36, self.team_color)
        self.draw_text_line(ref.center(22), 22, refx, 48, self.team_color)


    def draw96(self):
        if self.countdown > 0:
            next_match = f'NEXT: {int(self.countdown/60):2}:{(self.countdown%60):02}'
        else:
            next_match = "NEXT MATCH:"

        try:
            team1 = self.team1[0:22]
        except:
            team1 = 'TBD'
        try:
            team2 = self.team2[0:22]
        except:
            team2 = 'TBD'
        try:
            ref = f'REF: {self.ref}'[0:22]
        except:
            ref = 'REF: TBD'

        nextx = 8 if (len(next_match) % 2 == 0) else 14
        team1x = 8 if (len(team1) % 2 == 0) else 14
        team2x = 8 if (len(team2) % 2 == 0) else 14
        refx = 8 if (len(ref) % 2 == 0) else 14

        self.clear()
        self.draw_text_line(next_match.center(22), 22, nextx, -1, self.next_match_color)
        self.draw_text_line(team1.center(22), 22, team1x, 19, self.team_color)
        self.draw_text_line("VS".center(22), 22, 8, 38, self.team_color)
        self.draw_text_line(team2.center(22), 22, team2x, 57, self.team_color)
        self.draw_text_line(ref.center(22), 22, refx, 76, self.team_color)
