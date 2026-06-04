#!/usr/bin/env python3

import sys
from multiprocessing.connection import Client

def main():
    connection = Client(('127.0.0.1', 5900), authkey=b'vbscores')
    connection.send({'cmd': sys.argv[1], 'data': sys.argv[2]})
