
from PIL import Image, ImageDraw, ImageFont
from .periodic import periodic_task

class TimerScreen:
    def __init__(self, name, config):
        self.timer = None
        self.name = name
        self.visible = False
        self.cols = config.screen_cols()
        self.rows = config.screen_rows()
        self.resource_path = config.display.get("resource_path", "/usr/share/scoreboard")
        self.mesg_color = (255,191,0)
        self.timer_color = (255,0,0)
        self.duration = 0
        self.count = 0
        self.running = True
        self.autohide = 0
        self.autohide_count = 0
        if self.rows == 32:
            self.mesg_font = ImageFont.load(self.resource_path + '/fonts/6x12.pil')
            self.timer_font = ImageFont.load(self.resource_path + '/fonts/9x18B.pil')
            self.draw = self.draw32
        elif self.rows == 96:
            self.mesg_font = ImageFont.truetype('VeraMono.ttf', 21)
            self.timer_font = ImageFont.truetype('VeraMono.ttf', 30)
            self.draw = self.draw96
        else:
            self.mesg_font = ImageFont.truetype('VeraMono.ttf', 16)
            self.timer_font = ImageFont.truetype('VeraMono.ttf', 25)
            self.draw = self.draw64


    def clear(self):
        self.image = Image.new('RGB', (self.cols,self.rows))
        self.img_draw = ImageDraw.Draw(self.image)


    @periodic_task(1)
    def update(iteration, self, **kwargs):
        self.draw(kwargs.get('mesg'), self.count)
        if kwargs.get('display'): kwargs['display'].update()

        if self.duration < 0:
            if self.running: self.count += 1
        elif self.count <= 0:
            if self.autohide:
                self.autohide_count += 1
                if self.autohide_count >= self.autohide: self.hide(**kwargs)
        else:
            if self.running: self.count -= 1


    def show(self, **kwargs):
        self.duration = kwargs['duration']
        self.autohide = kwargs.get('autohide', 0)
        self.visible = True
        if self.timer == None:
            self.reset()
            self.running = True
            self.autohide_count = 0
            self.timer = self.update(**kwargs)


    def hide(self, **kwargs):
        self.visible = False
        if self.timer:
            self.timer.set()
            self.timer = None
        if kwargs.get('display'): kwargs['display'].update()


    def pause(self):
        self.running = not self.running


    def reset(self):
        self.count = self.duration
        if self.count < 0: self.count = 0


    def draw32(self, msg, count):
        self.clear()
        if msg:
            [x,l] = [1,16] if (len(msg) % 2 == 0) else [3,15]
            self.img_draw.text((x,1), msg.center(l), font=self.mesg_font, fill=self.mesg_color)

            msg2 = '{:2}:{:02}'.format(*divmod(count,60))
            [x,l] = [8,9] if (len(msg2) % 2 == 0) else [3,10]
            self.img_draw.text((x,12), msg2.center(l), font=self.timer_font, fill=self.timer_color)
        else:
            msg2 = '{:2}:{:02}'.format(*divmod(count,60))
            [x,l] = [8,9] if (len(msg2) % 2 == 0) else [3,10]
            self.img_draw.text((x,8), msg2.center(l), font=self.timer_font, fill=self.timer_color)


    def draw64(self, msg, count):
        self.clear()
        if msg:
            [x,l] = [6,18] if (len(msg) % 2 == 0) else [1,19]
            self.img_draw.text((x,8), msg.center(l), font=self.mesg_font, fill=self.mesg_color)

            msg2 = '{:2}:{:02}'.format(*divmod(count,60))
            [x,l] = [10,11] if (len(msg2) % 2 == 0) else [2,12]
            self.img_draw.text((x,30), msg2.center(l), font=self.timer_font, fill=self.timer_color)
        else:
            msg2 = '{:2}:{:02}'.format(*divmod(count,60))
            [x,l] = [10,11] if (len(msg2) % 2 == 0) else [3,12]
            self.img_draw.text((x,18), msg2.center(l), font=self.timer_font, fill=self.timer_color)


    def draw96(self, msg, count):
        self.clear()
        if msg:
            msg = msg[0:20]
            [x,l] = [1,20] if (len(msg) % 2 == 0) else [7,19]
            self.img_draw.text((x,10), msg.center(l), font=self.mesg_font, fill=self.mesg_color)

            msg2 = '{:2}:{:02}'.format(*divmod(count,60))
            [x,l] = [15,12] if (len(msg2) % 2 == 0) else [10,13]
            self.img_draw.text((x,45), msg2.center(l), font=self.timer_font, fill=self.timer_color)
        else:
            msg2 = '{:2}:{:02}'.format(*divmod(count,60))
            [x,l] = [15,12] if (len(msg2) % 2 == 0) else [10,13]
            self.img_draw.text((x,30), msg2.center(l), font=self.timer_font, fill=self.timer_color)
