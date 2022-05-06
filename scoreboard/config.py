
from configparser import ConfigParser
import subprocess
from json import dumps


class Config:

    def __init__(self, config_file=None):
        self.config = ConfigParser()
        if config_file:
            self.archive = False
            self.file = config_file
        else:
            self.archive = True
            self.file = "/usr/share/scoreboard/sb_config"


    def load(self):
        if self.archive:
            subprocess.run(["tar", "xz",  "-f", "/dev/mmcblk0p4", "-C", "/usr/share/scoreboard"])
        self.read()


    def read(self):
        self.config.read_file(open(self.file))
        self.scoreboard = self.config["scoreboard"]
        self.display = self.config["display"]
        self.wifi = self.config["wifi"]


    def save(self):
        self.write()
        if self.archive:
            subprocess.run(["tar", "cz", "-f", "/dev/mmcblk0p4", "-C", "/usr/share/scoreboard", "sb_config"])


    def write(self):
        with open(self.file, "w") as configfile:
            self.config.write(configfile)


    def json(self):
        d = {}
        d['scoreboard'] = dict(self.scoreboard)
        d['display'] = dict(self.display)
        d['wifi'] = dict(self.wifi)
        return dumps(d)
