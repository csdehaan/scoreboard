#!/usr/bin/env python3

import sys
from scoreboard.display import rgb_display

def main():
    cfg_file = None
    if (len(sys.argv) > 1): cfg_file = sys.argv[1]

    rgb_display(cfg_file)
