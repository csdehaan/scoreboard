#!/usr/bin/env python3

import sys
from scoreboard.sb_online import sb_online

def main():
    try:
        sb_online(sys.argv[1])
    except IndexError:
        sb_online()
