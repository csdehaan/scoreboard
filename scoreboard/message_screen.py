
from PIL import Image, ImageDraw, ImageFont
from .periodic import periodic_task


class MessageScreen:
    def __init__(self, name, config):
        self.timer = None
        self.name = name
        self.visible = False
        self.cols = config.screen_cols()
        self.rows = config.screen_rows()
        self.resource_path = config.display.get("resource_path", "/usr/share/scoreboard")
        self.default_color = (255,191,0)
        if self.rows == 32:
            self.mesg_font = ImageFont.load(self.resource_path + '/fonts/6x12.pil')
            self.draw = self.draw32
        elif self.rows == 96:
            self.mesg_font = ImageFont.truetype('VeraMono.ttf', 21)
            self.draw = self.draw96
        else:
            self.mesg_font = ImageFont.truetype('VeraMono.ttf', 16)
            self.draw = self.draw64


    def clear(self):
        self.image = Image.new('RGB', (self.cols,self.rows))
        self.img_draw = ImageDraw.Draw(self.image)


    @periodic_task(1)
    def update(iteration, self, **kwargs):
        if kwargs['duration']-iteration <= 0:
            self.hide(**kwargs)


    @periodic_task(1)
    def update_timeout(iteration, self, **kwargs):
        count = kwargs['duration']-iteration
        if count <= 0:
            self.hide(**kwargs)
        else:
            self.draw([kwargs['mesg'][0], 'TIMEOUT', '{:01}:{:02}'.format(*divmod(count,60))])
            if kwargs.get('display'): kwargs['display'].update()


    @periodic_task(1)
    def update_workout(iteration, self, **kwargs):
        workout = kwargs['workout']
        if workout.in_progress():
            if workout.resting:
                if workout.exercise_rest() < 0:
                    self.draw([workout.exercise_name(), f'SET: {workout.current_set}', 'REST'])
                else:
                    self.draw([workout.exercise_name(), f'SET: {workout.current_set}', f'REST: {workout.time_remaining()}'])

            elif workout.exercise_type() == 'repetitions':
                self.draw([workout.exercise_name(), f'SET: {workout.current_set}', f'REPS: {workout.exercise_target()}'])
            elif workout.exercise_type() == 'duration':
                self.draw([workout.exercise_name(), f'SET: {workout.current_set}', f'TIME: {workout.time_remaining()}'])
            elif workout.exercise_type() == 'rest':
                self.draw([workout.exercise_name(), f'TIME: {workout.time_remaining()}'])
            if kwargs.get('display'): kwargs['display'].update()
            workout.tick()
        else:
            self.hide(**kwargs)


    def show(self, **kwargs):
        if kwargs.get('mesg'): self.draw(kwargs['mesg'])
        if self.timer == None:
            if kwargs.get('duration'):
                if kwargs.get('style') == 'timeout': self.timer = self.update_timeout(**kwargs)
                else: self.timer = self.update(**kwargs)
            if kwargs.get('workout'): self.timer = self.update_workout(**kwargs)
        self.visible = True
        if self.timer == None and kwargs.get('display'): kwargs['display'].update()


    def show_workout(self, workout):
        self.visible = True


    def hide(self, **kwargs):
        self.visible = False
        if self.timer:
            self.timer.set()
            self.timer = None
        if kwargs.get('display'): kwargs['display'].update()


    def get_msg_text(self, msg):
            if isinstance(msg, (list,tuple)):
                return((msg[0],msg[1]))
            else:
                return((msg,self.default_color))


    def draw32(self, msg):
        self.clear()
        if len(msg) == 1:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [3,15]
            self.img_draw.text((x,10), text.center(l), font=self.mesg_font, fill=color)
        if len(msg) == 2:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [3,15]
            self.img_draw.text((x,5), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[1])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [3,15]
            self.img_draw.text((x,15), text.center(l), font=self.mesg_font, fill=color)
        if len(msg) == 3:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [3,15]
            self.img_draw.text((x,0), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[1])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [3,15]
            self.img_draw.text((x,10), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[2])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [3,15]
            self.img_draw.text((x,20), text.center(l), font=self.mesg_font, fill=color)
        if len(msg) > 3:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [4,15]
            self.img_draw.text((x,-3), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[1])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [4,15]
            self.img_draw.text((x,5), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[2])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [4,15]
            self.img_draw.text((x,13), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[3])
            [x,l] = [1,16] if (len(text) % 2 == 0) else [4,15]
            self.img_draw.text((x,21), text.center(l), font=self.mesg_font, fill=color)


    def draw64(self, msg):
        self.clear()
        if len(msg) == 1:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [0,20] if (len(text) % 2 == 0) else [4,19]
            self.img_draw.text((x,22), text.center(l), font=self.mesg_font, fill=color)
        if len(msg) == 2:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [0,20] if (len(text) % 2 == 0) else [4,19]
            self.img_draw.text((x,10), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[1])
            [x,l] = [0,20] if (len(text) % 2 == 0) else [4,19]
            self.img_draw.text((x,32), text.center(l), font=self.mesg_font, fill=color)
        if len(msg) == 3:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [0,20] if (len(text) % 2 == 0) else [4,19]
            self.img_draw.text((x,3), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[1])
            [x,l] = [0,20] if (len(text) % 2 == 0) else [4,19]
            self.img_draw.text((x,23), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[2])
            [x,l] = [0,20] if (len(text) % 2 == 0) else [4,19]
            self.img_draw.text((x,43), text.center(l), font=self.mesg_font, fill=color)
        if len(msg) > 3:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [0,20] if (len(text) % 2 == 0) else [4,19]
            self.img_draw.text((x,0), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[1])
            [x,l] = [0,20] if (len(text) % 2 == 0) else [4,19]
            self.img_draw.text((x,15), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[2])
            [x,l] = [0,20] if (len(text) % 2 == 0) else [4,19]
            self.img_draw.text((x,30), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[3])
            [x,l] = [0,20] if (len(text) % 2 == 0) else [4,19]
            self.img_draw.text((x,45), text.center(l), font=self.mesg_font, fill=color)


    def draw96(self, msg):
        self.clear()
        if len(msg) == 1:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.img_draw.text((x,34), text.center(l), font=self.mesg_font, fill=color)
        if len(msg) == 2:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.img_draw.text((x,15), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[1])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.img_draw.text((x,48), text.center(l), font=self.mesg_font, fill=color)
        if len(msg) == 3:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.img_draw.text((x,4), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[1])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.img_draw.text((x,35), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[2])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.img_draw.text((x,66), text.center(l), font=self.mesg_font, fill=color)
        if len(msg) > 3:
            text, color = self.get_msg_text(msg[0])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.img_draw.text((x,1), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[1])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.img_draw.text((x,24), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[2])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.img_draw.text((x,47), text.center(l), font=self.mesg_font, fill=color)
            text, color = self.get_msg_text(msg[3])
            [x,l] = [1,20] if (len(text) % 2 == 0) else [7,19]
            self.img_draw.text((x,70), text.center(l), font=self.mesg_font, fill=color)
