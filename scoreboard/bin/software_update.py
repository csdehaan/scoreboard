#!/usr/bin/env python3

import sys
from scoreboard.software_update import software_update

def main():
    force_update = len(sys.argv) > 1 and sys.argv[1] == 'force'
    software_update(force_update)
