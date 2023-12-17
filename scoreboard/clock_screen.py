
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from .periodic import periodic_task

class ClockScreen:
    def __init__(self, name, config):
        self.timer = None
        self.name = name
        self.visible = False
        self.cols = config.screen_cols()
        self.rows = config.screen_rows()
        self.resource_path = config.display.get("resource_path", "/usr/share/scoreboard")
        self.load_logo(config.display["logo"])
        self.court = config.scoreboard["court"]
        self.court_color = (255,0,0)
        self.time_color = (255,0,0)
        if self.rows == 32:
            self.court_font = ImageFont.load(self.resource_path + '/fonts/7x13B.pil')
            self.time_font = ImageFont.load(self.resource_path + '/fonts/9x18B.pil')
            self.draw = self.draw32
        elif self.rows == 96:
            self.court_font = ImageFont.truetype('VeraMono.ttf', 28)
            self.time_font = ImageFont.truetype('VeraMono.ttf', 30)
            self.draw = self.draw96
        else:
            self.court_font = ImageFont.truetype('VeraMono.ttf', 20)
            self.time_font = ImageFont.truetype('VeraMono.ttf', 25)
            self.draw = self.draw64


    def clear(self):
        self.image = Image.new('RGB', (self.cols,self.rows))
        self.img_draw = ImageDraw.Draw(self.image)


    def load_logo(self, org):
        size = self.rows
        try:
            self.logo = Image.open(f'/media/data/logo/{org}{size}.png').convert('RGB')
        except:
            self.logo = Image.open(f'{self.resource_path}/vbs{size}.png').convert('RGB')


    @periodic_task(10)
    def update(iteration, self, **kwargs):
        self.draw()
        if kwargs.get('display'): kwargs['display'].update()


    def run(self, display):
        self.visible = True
        if self.timer == None:
            self.timer = self.update(display=display)


    def stop(self):
        if self.timer:
            self.timer.set()
            self.timer = None


    def draw32(self):
        self.clear()
        self.image.paste(self.logo)

        court_txt = f'COURT {self.court}'[0:9]
        courtx = 36 if len(court_txt) % 2 == 0 else 33
        self.img_draw.text((courtx,2), court_txt.center(9), font=self.court_font, fill=self.court_color)

        time = datetime.now().strftime("%-I:%M")
        timex = 46 if len(time) % 2 == 0 else 41
        self.img_draw.text((timex,14), time, font=self.time_font, fill=self.time_color)


    def draw64(self):
        self.clear()
        self.image.paste(self.logo)

        court_txt = f'COURT {self.court}'[0:9]
        courtx = 69 if len(court_txt) % 2 == 0 else 75
        self.img_draw.text((courtx,7), court_txt.center(9), font=self.court_font, fill=self.court_color)

        time = datetime.now().strftime("%-I:%M")
        timex = 99 if len(time) % 2 == 0 else 92
        self.img_draw.text((timex,30), time, font=self.time_font, fill=self.time_color)


    def draw96(self):
        self.clear()
        self.image.paste(self.logo)

        court_txt = f'COURT {self.court}'[0:9]
        courtx = 92 if len(court_txt) % 2 == 0 else 100
        self.img_draw.text((courtx,10), court_txt.center(9), font=self.court_font, fill=self.court_color)

        time = datetime.now().strftime("%-I:%M")
        timex = 140 if len(time) % 2 == 0 else 131
        self.img_draw.text((timex,48), time, font=self.time_font, fill=self.time_color)
