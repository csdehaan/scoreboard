
from datetime import datetime
from multiprocessing.connection import Listener
from threading import Thread

from scoreboard import Config

from PyQt5 import Qt, QtCore, QtWidgets

class Display(Qt.QApplication):

    def __init__(self, config):
        super().__init__([])
        self.win = Qt.QDialog()
        self.win.resize(500, 150)
        self.win.move(config.display.getint("window_x", 100), config.display.getint("window_y", 100))
        self.main_layout = QtWidgets.QVBoxLayout(self.win)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.score_widget = QtWidgets.QWidget(self.win)
        self.main_layout.addWidget(self.score_widget)
        self.score_layout = QtWidgets.QHBoxLayout(self.score_widget)
        self.score_layout.setContentsMargins(0, 0, 0, 0)
        self.server = QtWidgets.QVBoxLayout()
        self.server11 = QtWidgets.QLabel(self.score_widget)
        self.server11.setMaximumSize(QtCore.QSize(20, 300))
        self.server11.setText("*")
        self.server.addWidget(self.server11)
        self.server12 = QtWidgets.QLabel(self.score_widget)
        self.server12.setMaximumSize(QtCore.QSize(20, 300))
        self.server.addWidget(self.server12)
        self.server13 = QtWidgets.QLabel(self.score_widget)
        self.server13.setMaximumSize(QtCore.QSize(20, 300))
        self.server.addWidget(self.server13)
        self.server14 = QtWidgets.QLabel(self.score_widget)
        self.server14.setMaximumSize(QtCore.QSize(20, 300))
        self.server.addWidget(self.server14)
        line = QtWidgets.QFrame(self.score_widget)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.server.addWidget(line)
        self.server21 = QtWidgets.QLabel(self.score_widget)
        self.server21.setMaximumSize(QtCore.QSize(20, 300))
        self.server.addWidget(self.server21)
        self.server22 = QtWidgets.QLabel(self.score_widget)
        self.server22.setMaximumSize(QtCore.QSize(20, 300))
        self.server.addWidget(self.server22)
        self.server23 = QtWidgets.QLabel(self.score_widget)
        self.server23.setMaximumSize(QtCore.QSize(20, 300))
        self.server.addWidget(self.server23)
        self.server24 = QtWidgets.QLabel(self.score_widget)
        self.server24.setMaximumSize(QtCore.QSize(20, 300))
        self.server.addWidget(self.server24)
        self.score_layout.addLayout(self.server)
        self.players = QtWidgets.QVBoxLayout()
        self.player11 = QtWidgets.QLabel(self.score_widget)
        self.player11.setText("Player 1")
        self.players.addWidget(self.player11)
        self.player12 = QtWidgets.QLabel(self.score_widget)
        self.player12.setText("Player 2")
        self.players.addWidget(self.player12)
        self.player13 = QtWidgets.QLabel(self.score_widget)
        self.player13.setText("Player 3")
        self.players.addWidget(self.player13)
        self.player14 = QtWidgets.QLabel(self.score_widget)
        self.player14.setText("Player 4")
        self.players.addWidget(self.player14)
        line = QtWidgets.QFrame(self.score_widget)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.players.addWidget(line)
        self.player21 = QtWidgets.QLabel(self.score_widget)
        self.player21.setText("Player I")
        self.players.addWidget(self.player21)
        self.player22 = QtWidgets.QLabel(self.score_widget)
        self.player22.setText("Player II")
        self.players.addWidget(self.player22)
        self.player23 = QtWidgets.QLabel(self.score_widget)
        self.player23.setText("Player III")
        self.players.addWidget(self.player23)
        self.player24 = QtWidgets.QLabel(self.score_widget)
        self.player24.setText("Player IV")
        self.players.addWidget(self.player24)
        self.score_layout.addLayout(self.players)
        self.scores = QtWidgets.QVBoxLayout()
        self.team1_score = QtWidgets.QLCDNumber(self.score_widget)
        self.team1_score.setMaximumSize(QtCore.QSize(70, 300))
        self.team1_score.setLineWidth(0)
        self.team1_score.setDigitCount(2)
        self.scores.addWidget(self.team1_score)
        line = QtWidgets.QFrame(self.score_widget)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.scores.addWidget(line)
        self.team2_score = QtWidgets.QLCDNumber(self.score_widget)
        self.team2_score.setMaximumSize(QtCore.QSize(70, 300))
        self.team2_score.setLineWidth(0)
        self.team2_score.setDigitCount(2)
        self.scores.addWidget(self.team2_score)
        self.score_layout.addLayout(self.scores)

        self.mesg_widget = QtWidgets.QWidget(self.win)
        self.main_layout.addWidget(self.mesg_widget)
        self.mesg_layout = QtWidgets.QVBoxLayout(self.mesg_widget)
        self.mesg_layout.setContentsMargins(0, 0, 0, 0)
        self.mesg1 = QtWidgets.QLabel(self.mesg_widget)
        self.mesg1.setAlignment(Qt.Qt.AlignCenter)
        self.mesg_layout.addWidget(self.mesg1)
        self.mesg2 = QtWidgets.QLabel(self.mesg_widget)
        self.mesg2.setAlignment(Qt.Qt.AlignCenter)
        self.mesg_layout.addWidget(self.mesg2)
        self.mesg3 = QtWidgets.QLabel(self.mesg_widget)
        self.mesg3.setAlignment(Qt.Qt.AlignCenter)
        self.mesg_layout.addWidget(self.mesg3)
        self.mesg4 = QtWidgets.QLabel(self.mesg_widget)
        self.mesg4.setAlignment(Qt.Qt.AlignCenter)
        self.mesg_layout.addWidget(self.mesg4)
        self.mesg_widget.hide()

        self.court = config.scoreboard["court"]


    def update_match(self, match):
        self.player11.setText(match.player(1,1))
        if match.player(1,2) == '':
            self.player12.setHidden(True)
            self.server12.setHidden(True)
        else:
            self.player12.setText(match.player(1,2))
            self.player12.setHidden(False)
            self.server12.setHidden(False)
        if match.player(1,3) == '':
            self.player13.setHidden(True)
            self.server13.setHidden(True)
        else:
            self.player13.setText(match.player(1,3))
            self.player13.setHidden(False)
            self.server13.setHidden(False)
        if match.player(1,4) == '':
            self.player14.setHidden(True)
            self.server14.setHidden(True)
        else:
            self.player14.setText(match.player(1,4))
            self.player14.setHidden(False)
            self.server14.setHidden(False)
        self.player21.setText(match.player(2,1))
        if match.player(2,2) == '':
            self.player22.setHidden(True)
            self.server22.setHidden(True)
        else:
            self.player22.setText(match.player(2,2))
            self.player22.setHidden(False)
            self.server22.setHidden(False)
        if match.player(2,3) == '':
            self.player23.setHidden(True)
            self.server23.setHidden(True)
        else:
            self.player23.setText(match.player(2,3))
            self.player23.setHidden(False)
            self.server23.setHidden(False)
        if match.player(2,4) == '':
            self.player24.setHidden(True)
            self.server24.setHidden(True)
        else:
            self.player24.setHidden(False)
            self.server24.setHidden(False)
            self.player24.setText(match.player(2,4))
        self.server11.setText("*" if match.server() == 11 else "")
        self.server12.setText("*" if match.server() == 12 else "")
        self.server13.setText("*" if match.server() == 13 else "")
        self.server14.setText("*" if match.server() == 14 else "")
        self.server21.setText("*" if match.server() == 21 else "")
        self.server22.setText("*" if match.server() == 22 else "")
        self.server23.setText("*" if match.server() == 23 else "")
        self.server24.setText("*" if match.server() == 23 else "")
        self.team1_score.display(match.team1_score())
        self.team2_score.display(match.team2_score())
        self.mesg_widget.hide()
        self.score_widget.show()


    def update_clock(self):
        court = f'COURT {self.court}'[0:9]
        current_time = datetime.now().strftime("%I:%M")
        self.mesg1.setText("")
        self.mesg2.setText(court)
        self.mesg3.setText(current_time)
        self.mesg4.setText("")
        self.score_widget.hide()
        self.mesg_widget.show()


    def update_next_match(self, teams, countdown=-1):
        if int(countdown) > 0:
            next_match = f'NEXT: {int(countdown/60):2}:{(int(countdown)%60):02}'.center(16)
        else:
            next_match = "NEXT MATCH:".center(16)

        try:
            team1 = teams[0][0:16]
        except:
            team1 = 'TBD'
        try:
            team2 = teams[1][0:16]
        except:
            team2 = 'TBD'

        self.mesg1.setText(next_match)
        self.mesg2.setText(team1)
        self.mesg3.setText("VS")
        self.mesg4.setText(team2)
        self.score_widget.hide()
        self.mesg_widget.show()


    def show_message(self, msg):
        if len(msg) == 1:
            self.mesg1.setText("")
            self.mesg2.setText(msg[0])
            self.mesg3.setText("")
        if len(msg) == 2:
            self.mesg1.setText(msg[0])
            self.mesg2.setText(msg[1])
            self.mesg3.setText("")
        if len(msg) == 3:
            self.mesg1.setText(msg[0])
            self.mesg2.setText(msg[1])
            self.mesg3.setText(msg[2])
        self.mesg4.setText("")
        self.score_widget.hide()
        self.mesg_widget.show()


def listen(disp, port):
    display = disp
    listener = Listener(('localhost', port), authkey=b'vbscores')
    running = True
    while running:
        conn = listener.accept()

        try:
            while True:
                msg = conn.recv()
                if msg[0] == 'clock':
                    display.update_clock()
                if msg[0] == 'match':
                    display.update_match(msg[1])
                if msg[0] == 'next_match':
                    display.update_next_match(msg[1], msg[2])
                if msg[0] == 'court':
                    display.court = msg[1]
                if msg[0] == 'logo':
                    display.load_logo(msg[1])
                if msg[0] == 'mesg':
                    display.show_message(msg[1:4])
                if msg[0] == 'close':
                    conn.close()
                    break
                if msg[0] == 'shutdown':
                    print('Shutting down display listener')
                    conn.close()
                    running = False
                    break
        except Exception as e:
            print(e)

    listener.close()


def qt_display(config_file):
    config = Config(config_file)
    config.read()

    display = Display(config)

    listen_thread = Thread(target=listen, args=(display,config.display.getint("port", 6000)))
    listen_thread.start()

    display.win.show()
    display.exec_()
