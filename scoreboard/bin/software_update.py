#!/usr/bin/env python3

import sys
from scoreboard.software_update import software_update

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'force':
        software_update(True)
    else:
        software_update(False)
