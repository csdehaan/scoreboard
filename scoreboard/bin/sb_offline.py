#!/usr/bin/env python3

import sys
from scoreboard.sb_offline import sb_offline

def main():
    try:
        sb_offline(sys.argv[1])
    except IndexError:
        sb_offline()
