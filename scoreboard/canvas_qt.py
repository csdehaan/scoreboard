
from bdfparser import Font
from PIL import Image, ImageDraw
from datetime import datetime
from PyQt5 import Qt, QtCore


class RgbLed(Qt.QWidget):
    clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(10,10)
        self.setMaximumSize(300,300)
        self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)
        self.off()

    def paintEvent(self, event):
        painter = Qt.QPainter(self)
        painter.setRenderHint(Qt.QPainter.Antialiasing, True)
        rect = self.rect().adjusted(1,1,-1,-1)
        hilite = Qt.QPoint(int(rect.width()/2), int(rect.height()/4))
        gradient = Qt.QRadialGradient(hilite, rect.width() * 0.75, hilite)
        painter.setBrush(Qt.QBrush(gradient))
        gradient.setColorAt(1.0, self.color)
        painter.setBrush(Qt.QBrush(gradient))
        painter.drawEllipse(rect)

    def setSize(self, size):
        self.setFixedSize(size, size)

    def on(self, color):
        self.color = color
        self.update()

    def off(self):
        self.on(Qt.QColor('black'))


class Canvas(Qt.QApplication):

    def __init__(self, config):
        super().__init__([])
        self.win = Qt.QMainWindow()
        self.win.resize(1920, 640)
        self.win.move(config.display.getint("window_x", 100), config.display.getint("window_y", 100))
        self.win.setStyleSheet('background-color: black;')
        self.win.setAutoFillBackground( True )
        self.rows = 64
        self.cols = 192
        self.resource_path = config.display.get("resource_path", "/usr/share/scoreboard")
        self.load_logo(config.display["logo"])
        self.court = config.scoreboard["court"]
        self.canvas = Image.new('RGB', (192,64))

        # fonts
        self.court_font = Font(self.resource_path + "/fonts/BVM-20.bdf")
        self.time_font = Font(self.resource_path + "/fonts/BVM-25.bdf")
        self.player_name_font = Font(self.resource_path + "/fonts/BVM-12.bdf")
        self.score_font = Font(self.resource_path + "/fonts/BVM-25.bdf")
        self.mesg_font = Font(self.resource_path + "/fonts/BVM-16.bdf")

        # colors
        self.court_color = { 0: b'\x00\x00\x00', 1: b'\xff\x00\x00', 2: b'\x00\xff\x00' }
        self.time_color = { 0: b'\x00\x00\x00', 1: b'\xff\x00\x00', 2: b'\x00\xff\x00' }
        self.player_name_color = { 0: b'\x00\x00\x00', 1: b'\xff\xbf\x00', 2: b'\x00\xff\x00' }
        self.server_color = { 0: b'\x00\x00\x00', 1: b'\x00\xff\x00', 2: b'\x00\xff\x00' }
        self.score_color = { 0: b'\x00\x00\x00', 1: b'\xff\x00\x00', 2: b'\x00\xff\x00' }
        self.divide_line_color = { 0: b'\x00\x00\x00', 1: b'\x00\x00\xff', 2: b'\x00\xff\x00' }
        self.mesg_color = { 0: b'\x00\x00\x00', 1: b'\xff\xbf\x00', 2: b'\x00\xff\x00' }

        # leds
        self.leds = []
        for row in range(64):
            self.leds.append([])
            for col in range(192):
                self.leds[row].append(RgbLed(self.win))
                self.leds[row][col].setSize(10)
                self.leds[row][col].move(col*10, row*10)


    def run(self):
        self.win.show()
        self.exec_()


    def update(self):
        for row in range(64):
            for col in range(192):
                pixel = self.canvas.getpixel((col,row))
                self.leds[row][col].on(Qt.QColor(pixel[0], pixel[1], pixel[2]))


    def load_logo(self, org):
        try:
            self.logo = Image.open(f'{self.resource_path}/{org}64.png').convert('RGB')
        except:
            self.logo = Image.open(f'{self.resource_path}/vbs64.png').convert('RGB')


    def draw_text(self, font, x, y, color, text):
        render = font.draw(text)
        mody = y - render.height()
        img = Image.frombytes('RGB', (render.width(), render.height()), render.tobytes('RGB', color))
        self.canvas.paste(img, box=(x,mody))


    def draw_player_name(self, name, max_length, x, y, server):
        if name == None: return
        name = name[0:max_length]
        color = self.player_name_color
        if server: color = self.server_color
        self.draw_text(self.player_name_font, x, y+2, color, name)


    def draw_score(self, score, x, y):
        self.draw_text(self.score_font, x, y+5, self.score_color, str(score).rjust(2))


    def update_clock(self):
        self.canvas = Image.new('RGB', (192,64))
        self.canvas.paste(self.logo)

        court_txt = f'COURT {self.court}'[0:9]
        courtx = 69 if len(court_txt) % 2 == 0 else 75
        self.draw_text(self.court_font, courtx, 25+4, self.court_color, court_txt.center(9))

        time = datetime.now().strftime("%-I:%M")
        timex = 99 if len(time) % 2 == 0 else 92
        self.draw_text(self.time_font, timex, 53+5, self.time_color, time)

        self.update()



    def update_match(self, match):
        self.canvas = Image.new('RGB', (192,64))
        if match.player(1,3):
            self.draw_player_name(match.player(1, 1), 10, 2, 11, match.server() == 11)
            self.draw_player_name(match.player(1, 3), 10, 80, 11, match.server() == 13)
        else:
            self.draw_player_name(match.player(1, 1), 20, 2, 11, match.server() == 11)

        if match.player(1,4):
            self.draw_player_name(match.player(1, 2), 10, 2, 28, match.server() == 12)
            self.draw_player_name(match.player(1, 4), 10, 80, 28, match.server() == 14)
        else:
            self.draw_player_name(match.player(1, 2), 20, 2, 28, match.server() == 12)

        if match.player(2,3):
            self.draw_player_name(match.player(2, 1), 10, 2, 44, match.server() == 21)
            self.draw_player_name(match.player(2, 3), 10, 80, 44, match.server() == 23)
        else:
            self.draw_player_name(match.player(2, 1), 20, 2, 44, match.server() == 21)

        if match.player(2,4):
            self.draw_player_name(match.player(2, 2), 10, 2, 60, match.server() == 22)
            self.draw_player_name(match.player(2, 4), 10, 80, 60, match.server() == 24)
        else:
            self.draw_player_name(match.player(2, 2), 20, 2, 60, match.server() == 22)

        self.draw_score(match.team1_score(), 160, 23)
        self.draw_score(match.team2_score(), 160, 55)

        draw = ImageDraw.Draw(self.canvas)
        if match.team1_sets() > 0:
            draw.pieslice([(181,25),(185,29)], start=0.0, end=360.0, fill=(0,255,0), outline=(0,255,0))

        if match.team1_sets() > 1:
            draw.pieslice([(171,25),(175,29)], start=0.0, end=360.0, fill=(0,255,0), outline=(0,255,0))

        if match.team2_sets() > 0:
            draw.pieslice([(181,57),(185,61)], start=0.0, end=360.0, fill=(0,255,0), outline=(0,255,0))

        if match.team2_sets() > 1:
            draw.pieslice([(171,57),(175,61)], start=0.0, end=360.0, fill=(0,255,0), outline=(0,255,0))

        draw.line([(0,32),(191,32)], fill=(0,0,255), width=1)
        self.update()


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

        self.canvas = Image.new('RGB', (192,64))
        self.draw_player_name(next_match.center(26), 26, nextx, 10, True)
        self.draw_player_name(team1.center(26), 26, team1x, 23, False)
        self.draw_player_name("VS".center(26), 26, 4, 36, False)
        self.draw_player_name(team2.center(26), 26, team2x, 49, False)
        self.draw_player_name(ref.center(26), 26, refx, 62, False)
        self.update()


    def show_message(self, msg):
        self.canvas = Image.new('RGB', (192,64))
        if len(msg) == 1:
            [x,l] = [6,18] if (len(msg[0]) % 2 == 0) else [1,19]
            self.draw_text(self.mesg_font, x, 36+2, self.mesg_color, msg[0].center(l))
        if len(msg) == 2:
            [x,l] = [6,18] if (len(msg[0]) % 2 == 0) else [1,19]
            self.draw_text(self.mesg_font, x, 28+2, self.mesg_color, msg[0].center(l))
            [x,l] = [6,18] if (len(msg[1]) % 2 == 0) else [1,19]
            self.draw_text(self.mesg_font, x, 48+2, self.mesg_color, msg[1].center(l))
        if len(msg) == 3:
            [x,l] = [6,18] if (len(msg[0]) % 2 == 0) else [1,19]
            self.draw_text(self.mesg_font, x, 18+2, self.mesg_color, msg[0].center(l))
            [x,l] = [6,18] if (len(msg[1]) % 2 == 0) else [1,19]
            self.draw_text(self.mesg_font, x, 38+2, self.mesg_color, msg[1].center(l))
            [x,l] = [6,18] if (len(msg[2]) % 2 == 0) else [1,19]
            self.draw_text(self.mesg_font, x, 58+2, self.mesg_color, msg[2].center(l))
        if len(msg) > 3:
            [x,l] = [6,18] if (len(msg[0]) % 2 == 0) else [1,19]
            self.draw_text(self.mesg_font, x, 14+2, self.mesg_color, msg[0].center(l))
            [x,l] = [6,18] if (len(msg[1]) % 2 == 0) else [1,19]
            self.draw_text(self.mesg_font, x, 30+2, self.mesg_color, msg[1].center(l))
            [x,l] = [6,18] if (len(msg[2]) % 2 == 0) else [1,19]
            self.draw_text(self.mesg_font, x, 46+2, self.mesg_color, msg[2].center(l))
            [x,l] = [6,18] if (len(msg[3]) % 2 == 0) else [1,19]
            self.draw_text(self.mesg_font, x, 62+2, self.mesg_color, msg[3].center(l))
        self.update()


    def show_timer(self, msg, count):
        self.canvas = Image.new('RGB', (192,64))
        if msg:
            [x,l] = [6,18] if (len(msg) % 2 == 0) else [1,19]
            self.draw_text(self.mesg_font, x, 28+2, self.mesg_color, msg.center(l))

            msg2 = f'{int(count/60):2}:{(int(count)%60):02}'
            [x,l] = [10,12] if (len(msg2) % 2 == 0) else [3,13]
            self.draw_text(self.time_font, x, 48+5, self.score_color, msg2.center(l))
        else:
            msg2 = f'{int(count/60):2}:{(int(count)%60):02}'
            [x,l] = [10,12] if (len(msg2) % 2 == 0) else [3,13]
            self.draw_text(self.time_font, x, 36+5, self.score_color, msg2.center(l))
        self.update()
