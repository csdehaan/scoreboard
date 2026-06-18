#!/usr/bin/env python3

import sys
from scoreboard.scoreboard import Scoreboard

def main():
    mode = sys.argv[1]
    cfg_file = None
    if (len(sys.argv) > 2): cfg_file = sys.argv[2]

    Scoreboard.start(mode, cfg_file)
