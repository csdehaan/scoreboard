
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from .periodic import periodic_task

class NextMatchScreen:
    def __init__(self, name, config):
        self.timer = None
        self.name = name
        self.visible = False
        self.court = config.scoreboard["court"]
        self.cols = config.screen_cols()
        self.rows = config.screen_rows()
        self.resource_path = config.display.get("resource_path", "/usr/share/scoreboard")
        self.team_color = (255,191,0)
        self.next_match_color = (0,255,0)
        self.time_color = (255,0,0)
        self.team1 = 'TBD'
        self.team2 = 'TBD'
        self.ref = 'TBD'
        self.countdown = -1
        self.style = 'match'
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
        if kwargs.get('style') == 'reservation':
            self.style = 'reservation'
            self.reserved_for = kwargs['name']
            self.reservation_start = kwargs['start']
            self.reservation_end = kwargs['stop']
        else:
            self.style = 'match'
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
        if self.style == 'reservation':
            line1 = f'COURT {self.court}   {datetime.now().strftime("%-I:%M")}'
            line1_color = self.time_color

            line2 = 'RESERVED FOR'
            line2_color = self.next_match_color

            line3 = self.reserved_for[0:16]
            line3_color = self.next_match_color

            line4 = f'{self.reservation_start.strftime("%-I:%M")} - {self.reservation_end.strftime("%-I:%M")}'
            line4_color = self.next_match_color

        else:
            if self.countdown > 0:
                line1 = f'NEXT: {int(self.countdown/60):2}:{(self.countdown%60):02}'
            else:
                line1 = "NEXT MATCH:"

            try:
                line2 = self.team1[0:16]
            except:
                line2 = 'TBD'
            line3 = 'VS'
            try:
                line4 = self.team2[0:16]
            except:
                line4 = 'TBD'

            line1_color = self.next_match_color
            line2_color = self.team_color
            line3_color = self.team_color
            line4_color = self.team_color

        line1x = 0 if (len(line1) % 2 == 0) else 3
        line2x = 0 if (len(line2) % 2 == 0) else 3
        line3x = 0 if (len(line3) % 2 == 0) else 3
        line4x = 0 if (len(line4) % 2 == 0) else 3

        self.clear()
        self.draw_text_line(line1.center(16), 16, line1x, 2, line1_color)
        self.draw_text_line(line2.center(16), 16, line2x, 10, line2_color)
        self.draw_text_line(line3.center(16), 16, line3x, 18, line3_color)
        self.draw_text_line(line4.center(16), 16, line4x, 26, line4_color)


    def draw64(self):
        if self.style == 'reservation':
            line1 = f'COURT {self.court}   {datetime.now().strftime("%-I:%M")}'
            line1_color = self.time_color

            line2 = ''
            line2_color = self.next_match_color

            line3 = 'RESERVED FOR'
            line3_color = self.next_match_color

            line4 = self.reserved_for[0:26]
            line4_color = self.next_match_color

            line5 = f'{self.reservation_start.strftime("%-I:%M")} - {self.reservation_end.strftime("%-I:%M")}'
            line5_color = self.next_match_color

        else:
            if self.countdown > 0:
                line1 = f'NEXT: {int(self.countdown/60):2}:{(self.countdown%60):02}'
            else:
                line1 = "NEXT MATCH:"

            try:
                line2 = self.team1[0:26]
            except:
                line2 = 'TBD'
            line3 = 'VS'
            try:
                line4 = self.team2[0:26]
            except:
                line4 = 'TBD'
            try:
                line5 = f'REF: {self.ref}'[0:26]
            except:
                line5 = 'REF: TBD'

            line1_color = self.next_match_color
            line2_color = self.team_color
            line3_color = self.team_color
            line4_color = self.team_color
            line5_color = self.team_color

        line1x = 4 if (len(line1) % 2 == 0) else 8
        line2x = 4 if (len(line2) % 2 == 0) else 8
        line3x = 4 if (len(line3) % 2 == 0) else 8
        line4x = 4 if (len(line4) % 2 == 0) else 8
        line5x = 4 if (len(line5) % 2 == 0) else 8

        self.clear()
        self.draw_text_line(line1.center(22), 22, line1x, -1, line1_color)
        self.draw_text_line(line2.center(22), 22, line2x, 12, line2_color)
        self.draw_text_line(line3.center(22), 22, line3x, 24, line3_color)
        self.draw_text_line(line4.center(22), 22, line4x, 36, line4_color)
        self.draw_text_line(line5.center(22), 22, line5x, 48, line5_color)


    def draw96(self):
        if self.style == 'reservation':
            line1 = f'COURT {self.court}   {datetime.now().strftime("%-I:%M")}'
            line1_color = self.time_color

            line2 = ''
            line2_color = self.next_match_color

            line3 = 'RESERVED FOR'
            line3_color = self.next_match_color

            line4 = self.reserved_for[0:22]
            line4_color = self.next_match_color

            line5 = f'{self.reservation_start.strftime("%-I:%M")} - {self.reservation_end.strftime("%-I:%M")}'
            line5_color = self.next_match_color

        else:
            if self.countdown > 0:
                line1 = f'NEXT: {int(self.countdown/60):2}:{(self.countdown%60):02}'
            else:
                line1 = "NEXT MATCH:"

            try:
                line2 = self.team1[0:22]
            except:
                line2 = 'TBD'
            line3 = 'VS'
            try:
                line4 = self.team2[0:22]
            except:
                line4 = 'TBD'
            try:
                line5 = f'REF: {self.ref}'[0:22]
            except:
                line5 = 'REF: TBD'

            line1_color = self.next_match_color
            line2_color = self.team_color
            line3_color = self.team_color
            line4_color = self.team_color
            line5_color = self.team_color

        line1x = 8 if (len(line1) % 2 == 0) else 14
        line2x = 8 if (len(line2) % 2 == 0) else 14
        line3x = 8 if (len(line3) % 2 == 0) else 14
        line4x = 8 if (len(line4) % 2 == 0) else 14
        line5x = 8 if (len(line5) % 2 == 0) else 14

        self.clear()
        self.draw_text_line(line1.center(22), 22, line1x, -1, line1_color)
        self.draw_text_line(line2.center(22), 22, line2x, 19, line2_color)
        self.draw_text_line(line3.center(22), 22, line3x, 38, line3_color)
        self.draw_text_line(line4.center(22), 22, line4x, 57, line4_color)
        self.draw_text_line(line5.center(22), 22, line5x, 76, line5_color)
