
from PyQt5 import Qt
from .splash_screen import SplashScreen

LED_SIZE=8

class RgbLed:

    def __init__(self, x, y, size=LED_SIZE):
        self.x = x
        self.y = y
        self.setSize(size)
        self.off()

    def paint(self, painter):
        painter.setRenderHint(Qt.QPainter.Antialiasing, True)
        rect = self.rect().adjusted(1,1,-1,-1)
        hilite = Qt.QPoint(int(rect.width()/2), int(rect.height()/4))
        gradient = Qt.QRadialGradient(hilite, rect.width() * 0.75, hilite)
        painter.setBrush(Qt.QBrush(gradient))
        gradient.setColorAt(1.0, self.color)
        painter.setBrush(Qt.QBrush(gradient))
        painter.drawEllipse(rect)

    def rect(self):
        return Qt.QRect(self.x, self.y, self.size, self.size)

    def setSize(self, size):
        self.size = size

    def on(self, color):
        self.color = color

    def off(self):
        self.on(Qt.QColor('black'))


class LedDisplay(Qt.QMainWindow):
    def __init__(self, rows, cols):
        super().__init__()
        self.rows = rows
        self.cols = cols

        # leds
        self.leds = []
        for row in range(self.rows):
            self.leds.append([])
            for col in range(self.cols):
                self.leds[row].append(RgbLed(col*LED_SIZE, row*LED_SIZE))


    def show_img(self, image):
        for row in range(self.rows):
            for col in range(self.cols):
                pixel = image.getpixel((col,row))
                self.leds[row][col].on(Qt.QColor(pixel[0], pixel[1], pixel[2]))


    def paintEvent(self, event):
        painter = Qt.QPainter(self)
        for row in range(self.rows):
            for col in range(self.cols):
                self.leds[row][col].paint(painter)


class Display(Qt.QApplication):

    def __init__(self, config):
        super().__init__([])
        self.win = LedDisplay(config.screen_rows(), config.screen_cols())
        self.win.resize(config.screen_cols()*LED_SIZE, config.screen_rows()*LED_SIZE)
        self.win.move(config.display.getint("window_x", 100), config.display.getint("window_y", 100))
        self.win.setStyleSheet('background-color: black;')
        self.win.setAutoFillBackground( True )

        self.splash = SplashScreen('splash', config)
        self.show_splash("Starting")


    def run(self):
        self.win.show()
        self.exec_()


    def show(self, image):
        self.win.show_img(image)
        self.win.update()


    def show_splash(self, msg):
        self.splash.draw(msg)
        self.show(self.splash.image)
