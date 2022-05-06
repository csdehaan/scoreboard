
import setuptools
from Cython.Build import cythonize
from scoreboard.version import Version



setuptools.setup(
    name='scoreboard',
    version=Version.str(),
    description='VB Scores Scoreboard',
    long_description='',
    url='https://www.vb-scores.com',
    author='Craig DeHaan',
    author_email='csdehaan2@gmail.com',
    license='Other',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Games/Entertainment',
        'License :: Other/Proprietary License'
    ],
    packages=setuptools.find_packages(),
    scripts=['bin/cfg_update','bin/scoreboard','bin/software_update','bin/display','bin/sb_online','bin/sb_offline','bin/qt_display'],
    install_requires=['ActionCableZwei'],
    ext_modules = cythonize("scoreboard/*.py", language_level = "3")
)
