
from datetime import datetime
from multiprocessing.connection import Listener
from threading import Thread
import sys

from config import Config
from match import Match

from PyQt5 import Qt, QtCore, QtWidgets

class Display(Qt.QApplication):

    def __init__(self, config):
        super().__init__([])
        self.win = Qt.QDialog()
        self.win.resize(500, 150)
        self.main_layout = QtWidgets.QVBoxLayout(self.win)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.score_widget = QtWidgets.QWidget(self.win)
        self.main_layout.addWidget(self.score_widget)
        self.score_layout = QtWidgets.QHBoxLayout(self.score_widget)
        self.score_layout.setContentsMargins(0, 0, 0, 0)
        self.server = QtWidgets.QVBoxLayout()
        self.server1 = QtWidgets.QLabel(self.score_widget)
        self.server1.setMaximumSize(QtCore.QSize(20, 300))
        self.server1.setText("*")
        self.server.addWidget(self.server1)
        self.server2 = QtWidgets.QLabel(self.score_widget)
        self.server2.setMaximumSize(QtCore.QSize(20, 300))
        self.server.addWidget(self.server2)
        line = QtWidgets.QFrame(self.score_widget)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.server.addWidget(line)
        self.server3 = QtWidgets.QLabel(self.score_widget)
        self.server3.setMaximumSize(QtCore.QSize(20, 300))
        self.server.addWidget(self.server3)
        self.server4 = QtWidgets.QLabel(self.score_widget)
        self.server4.setMaximumSize(QtCore.QSize(20, 300))
        self.server.addWidget(self.server4)
        self.score_layout.addLayout(self.server)
        self.players = QtWidgets.QVBoxLayout()
        self.player1 = QtWidgets.QLabel(self.score_widget)
        self.player1.setText("Player 1")
        self.players.addWidget(self.player1)
        self.player2 = QtWidgets.QLabel(self.score_widget)
        self.player2.setText("Player 2")
        self.players.addWidget(self.player2)
        line = QtWidgets.QFrame(self.score_widget)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.players.addWidget(line)
        self.player3 = QtWidgets.QLabel(self.score_widget)
        self.player3.setText("Player 3")
        self.players.addWidget(self.player3)
        self.player4 = QtWidgets.QLabel(self.score_widget)
        self.player4.setText("Player 4")
        self.players.addWidget(self.player4)
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
        self.player1.setText(match.player1())
        self.player2.setText(match.player2())
        self.player3.setText(match.player3())
        self.player4.setText(match.player4())
        self.server1.setText("*" if match.server() == 1 else "")
        self.server2.setText("*" if match.server() == 2 else "")
        self.server3.setText("*" if match.server() == 3 else "")
        self.server4.setText("*" if match.server() == 4 else "")
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


def listen(disp):
    print('display listener')
    display = disp    
    listener = Listener(('localhost', 6000), authkey=b'vbscores')
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


config = Config(sys.argv[1])
config.read()

display = Display(config)

listen_thread = Thread(target=listen, args=(display,))
listen_thread.start()

display.win.show()
display.exec_()
