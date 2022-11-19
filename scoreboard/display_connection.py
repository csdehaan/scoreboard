
from time import sleep
from multiprocessing.connection import Client

class Display:
    def __init__(self, host, port):
        self.host = host
        self.port = port


    def send(self, mesg, timeout=1, max_tries=3):
        tries = 0
        ack = None
        connection = None
        while ack != 'ack' and tries < max_tries:
            try:
                connection = Client((self.host, self.port), authkey=b'vbscores')
                connection.send(mesg)
                if connection.poll(timeout):
                    ack = connection.recv()
            except Exception as e:
                print(f'display_connection exception (try={tries}): {type(e).__name__} - {e}')
                sleep(0.25)
            finally:
                tries = tries + 1
                if connection: connection.close()
