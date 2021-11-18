
from configparser import ConfigParser
import subprocess


class Config:

    def __init__(self):
        self.config = ConfigParser()


    def load(self):
        subprocess.run(["tar", "xz",  "-f", "/dev/mmcblk0p4", "-C", "/usr/share/scoreboard"])
        self.read()


    def read(self):
        self.config.read_file(open("/usr/share/scoreboard/sb_config"))
        self.scoreboard = self.config["scoreboard"]
        self.display = self.config["display"]
        self.wifi = self.config["wifi"]


    def save(self):
        self.write()
        subprocess.run(["tar", "cz", "-f", "/dev/mmcblk0p4", "-C", "/usr/share/scoreboard", "sb_config"])


    def write(self):
        with open("/usr/share/scoreboard/sb_config", "w") as configfile:
            self.config.write(configfile)

