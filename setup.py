
import setuptools
from Cython.Build import cythonize
from scoreboard.version import Version



setuptools.setup(
    name = 'scoreboard',
    version = Version.str(),
    description = 'VB Scores Scoreboard',
    long_description = '',
    url = 'https://www.vb-scores.com',
    author = 'Craig DeHaan',
    author_email = 'craig@vb-scores.com',
    license = 'Other',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Games/Entertainment',
        'License :: Other/Proprietary License'
    ],
    packages = setuptools.find_packages(),
    ext_modules = cythonize("scoreboard/*.py", exclude="scoreboard/gpio.py", language_level = "3"),
    entry_points = {
        'gui_scripts': [
            'cfg_update = scoreboard.bin.cfg_update:main',
            'scoreboard = scoreboard.bin.scoreboard:main',
            'software_update = scoreboard.bin.software_update:main',
            'display = scoreboard.bin.display:main',
            'sb_online = scoreboard.bin.sb_online:main',
            'sb_offline = scoreboard.bin.sb_offline:main'
        ]
    },
    install_requires = ['ActionCableZwei','Pillow']
)
