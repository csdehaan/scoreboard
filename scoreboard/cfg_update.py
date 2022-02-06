
import subprocess
from scoreboard import Config

def cfg_update(argv):
    cmd = argv[1]

    config = Config()
    config.read()
    config.config[argv[2]][argv[3]] = argv[4]

    if cmd == 'write':
        config.write()
    if cmd == 'save':
        config.save()
    if cmd == 'restart':
        config.save()
        subprocess.run(["killall", "sb_online"])
        subprocess.run(["killall", "sb_offline"])

