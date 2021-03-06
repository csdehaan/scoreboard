
import os
import urllib.request
import hashlib
import base64

from scoreboard import Config, Version
from scoreboard.api import Api
from scoreboard.display_connection import Display


def software_update(force):
    config = Config()
    config.read()

    api = Api(config.scoreboard["api_key"], config.scoreboard.getint('log_level', 10))
    sw = api.scoreboard_software()

    update = False
    if force: update = True
    if sw['major_version'] != 0:
        if Version.major != sw['major_version']: update = True
        if Version.minor != sw['minor_version']: update = True
        if Version.debug != sw['debug_version']: update = True

    if update:
        display = Display('localhost', config.display.getint("port", 6000))
        display.send(['mesg', 'Updating SW', f'{sw["major_version"]}.{sw["minor_version"]}.{sw["debug_version"]}', '', 'DO NOT TURN OFF'], 1, 8)

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
