
from PyQt5 import Qt
from .splash_screen import SplashScreen

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
        self.rows = config.screen_rows()
        self.cols = config.screen_cols()
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

        self.splash = SplashScreen('splash', config)
        self.show_splash("Starting")


    def run(self):
        self.win.show()
        self.exec_()


    def show(self, image):
        for row in range(self.rows):
            for col in range(self.cols):
                pixel = image.getpixel((col,row))
                self.leds[row][col].on(Qt.QColor(pixel[0], pixel[1], pixel[2]))


    def show_splash(self, msg):
        self.splash.draw(msg)
        self.show(self.splash.image)
