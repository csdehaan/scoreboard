#!/usr/bin/env python3

import sys
from scoreboard.display import rgb_display

def main():
    try:
        rgb_display(sys.argv[1])
    except IndexError:
        rgb_display()
