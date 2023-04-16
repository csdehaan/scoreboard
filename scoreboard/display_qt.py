
from PyQt5 import Qt

LED_SIZE=8

class RgbLed(Qt.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(5,5)
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


class Display(Qt.QApplication):

    def __init__(self, config):
        super().__init__([])
        self.rows = config.display.getint("rows", 64)
        self.cols = config.display.getint("cols", 192)
        self.win = Qt.QMainWindow()
        self.win.resize(self.cols*LED_SIZE, self.rows*LED_SIZE)
        self.win.move(config.display.getint("window_x", 100), config.display.getint("window_y", 100))
        self.win.setStyleSheet('background-color: black;')
        self.win.setAutoFillBackground( True )

        # leds
        self.leds = []
        for row in range(self.rows):
            self.leds.append([])
            for col in range(self.cols):
                self.leds[row].append(RgbLed(self.win))
                self.leds[row][col].setSize(LED_SIZE)
                self.leds[row][col].move(col*LED_SIZE, row*LED_SIZE)

        if self.cols == 256:
            from scoreboard.canvas_256x96 import Canvas
        elif self.cols == 192:
            from scoreboard.canvas_192x64 import Canvas
        else:
            from scoreboard.canvas_96x32 import Canvas
        self.canvas = Canvas(config)


    def run(self):
        self.win.show()
        self.exec_()


    def update(self):
        for row in range(self.rows):
            for col in range(self.cols):
                pixel = self.canvas.image.getpixel((col,row))
                self.leds[row][col].on(Qt.QColor(pixel[0], pixel[1], pixel[2]))


    def update_clock(self):
        self.canvas.update_clock()
        self.update()



    def update_match(self, match):
        self.canvas.update_match(match)
        self.update()


    def update_next_match(self, teams, countdown=-1):
        self.canvas.update_next_match(teams, countdown)
        self.update()


    def show_message(self, msg):
        self.canvas.show_message(msg)
        self.update()


    def show_timer(self, msg, count):
        self.canvas.show_timer(msg, count)
        self.update()


    def show_splash(self, msg):
        self.canvas.show_splash(msg)
        self.update()
