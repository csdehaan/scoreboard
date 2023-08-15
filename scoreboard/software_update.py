
import os
import urllib
import hashlib
import base64
from time import sleep

from scoreboard import Config, Version
from scoreboard.api import Api
from scoreboard.display_connection import Display
from scoreboard.message_screen import MessageScreen


def software_update(force):
    config = Config()
    config.read()
    update = False
    sw = None
    display = Display('127.0.0.1', config.display.getint("port", 6000))

    api = Api(config.scoreboard["api_key"], config.scoreboard.getint('log_level', 10))
    while sw == None:
        try:
            sw = api.scoreboard_software()
        except urllib.error.URLError as e:
            print(e)
            sleep(1)

    display.send(['splash', 'Updating'], 1, 8)

    if force: update = True
    if sw['major_version'] != 0:
        if Version.major != sw['major_version']: update = True
        if Version.minor != sw['minor_version']: update = True
        if Version.debug != sw['debug_version']: update = True


    if update:
        screen = MessageScreen("software_update", config)
        screen.draw(['Updating SW', f'{sw["major_version"]}.{sw["minor_version"]}.{sw["debug_version"]}', '', ['DO NOT TURN OFF',(255,0,0)]])
        display.send(screen.image, 1, 8)

        api.logger.info(f'Updating Scoreboard Software from {Version.str()} to {sw["major_version"]}.{sw["minor_version"]}.{sw["debug_version"]}')
        print("Running software update")

        api.logger.debug("Downloading")
        urllib.request.urlretrieve(sw['download_url'], "/tmp/sw_update.tgz")

        # verify checksum
        if str(sw['md5_hash']) != '':
            with open("/tmp/sw_update.tgz", "rb") as f:
                digest = hashlib.md5(f.read()).digest()
                if base64.b64encode(digest).decode() == sw['md5_hash']:
                    api.logger.info("Verified checksum")
                else:
                    api.logger.error(f'Failed to verify checksum ({base64.b64encode(digest).decode()})')
                    return

        api.logger.debug("Mounting Boot Drive")
        os.system("mkdir /media/boot")
        os.system("mount /dev/mmcblk0p1 /media/boot")

        api.logger.debug("Installing")
        os.system("tar -xf /tmp/sw_update.tgz -C /media/boot")

        if os.path.exists("/media/boot/post_install"):
            api.logger.info("Running post install script")
            os.system("/media/boot/post_install")
            os.remove("/media/boot/post_install")

        api.logger.debug("Rebooting")
        print("Done")
        os.system("umount /media/boot")
        os.system("reboot")

    else:
        print('No updates available')
