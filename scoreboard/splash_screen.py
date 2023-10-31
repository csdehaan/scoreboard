
from PIL import Image, ImageDraw, ImageFont

class SplashScreen:
    def __init__(self, name, config):
        self.name = name
        self.visible = False
        self.cols = config.screen_cols()
        self.rows = config.screen_rows()
        self.resource_path = config.display.get("resource_path", "/usr/share/scoreboard")
        self.load_logo(config.display["logo"])
        self.mesg_color = (0,255,0)
        self.vbs_color = (255,191,0)
        if self.rows == 32:
            self.mesg_font = ImageFont.load(self.resource_path + '/fonts/mono.pil')
            self.vbs_font = ImageFont.load(self.resource_path + '/fonts/6x12.pil')
            self.draw = self.draw32
        elif self.rows == 96:
            self.mesg_font = ImageFont.truetype('VeraMoBd.ttf', 18)
            self.vbs_font = ImageFont.truetype('VeraMono.ttf', 26)
            self.draw = self.draw96
        else:
            self.mesg_font = ImageFont.truetype('VeraMoBd.ttf', 14)
            self.vbs_font = ImageFont.truetype('VeraMono.ttf', 20)
            self.draw = self.draw64


    def clear(self):
        self.image = Image.new('RGB', (self.cols,self.rows))
        self.img_draw = ImageDraw.Draw(self.image)


    def load_logo(self, org):
        size = '' if (self.rows == 32) else self.rows
        try:
            self.logo = Image.open(f'{self.resource_path}/{org}{size}.png').convert('RGB')
        except:
            self.logo = Image.open(f'{self.resource_path}/vbs{size}.png').convert('RGB')


    def draw_text_line(self, text, max_length, x, y, color):
        if text == None: return
        text = text[0:max_length]
        self.img_draw.text((x,y), text, font=self.mesg_font, fill=color)


    def draw32(self, msg):
        self.clear()
        self.image.paste(self.logo)

        self.img_draw.text((38,2), "VB Scores", font=self.vbs_font, fill=self.vbs_color)
        mesgx = 29 if len(msg) % 2 == 0 else 32
        self.draw_text_line(msg.center(11), 11, mesgx, 22, self.mesg_color)


    def draw64(self, msg):
        self.clear()
        self.image.paste(self.logo)

        self.img_draw.text((75,5), "VB Scores", font=self.vbs_font, fill=self.vbs_color)
        mesgx = 60 if len(msg) % 2 == 0 else 64
        self.draw_text_line(msg.center(15), 15, mesgx, 38, self.mesg_color)


    def draw96(self, msg):
        self.clear()
        self.image.paste(self.logo)

        self.img_draw.text((107,15), "VB Scores", font=self.vbs_font, fill=self.vbs_color)
        mesgx = 89 if len(msg) % 2 == 0 else 95
        self.draw_text_line(msg.center(15), 15, mesgx, 55, self.mesg_color)
