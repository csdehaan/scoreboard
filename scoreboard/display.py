
from multiprocessing.connection import Listener
from scoreboard import Config
from threading import Thread
from PIL import Image


def listen(disp, port):
    display = disp
    listener = Listener(('127.0.0.1', port), authkey=b'vbscores')
    running = True
    while running:
        conn = listener.accept()

        try:
            msg = conn.recv()
            if isinstance(msg, Image.Image):
                display.show(msg)
                conn.send('ack')
            elif msg[0] == 'shutdown':
                print('Shutting down display listener')
                running = False
            elif msg[0] == 'splash':
                display.show_splash(msg[1])
                conn.send('ack')
            elif msg[0] == 'ping':
                conn.send('ack')
            else:
                conn.send('nack')
        except Exception as e:
            print(f'Display Exception: [{type(e).__name__}] - {e}')
        finally:
            conn.close()

    listener.close()



def rgb_display(config_file=None):
    config = Config(config_file)
    config.read()

    if config_file:
        from scoreboard.display_qt import Display
    else:
        from scoreboard.display_led import Display
    display = Display(config)

    if config_file:
        from scoreboard.display_connection import Display as Connection
        import psutil
        listen_thread = Thread(target=listen, args=(display,config.display.getint("port", 6000)))
        listen_thread.start()

        display.run()

        print('Qt Display closed. Waiting for listen thread to exit.')
        conn = Connection('127.0.0.1', config.display.getint("port", 6000))
        conn.send(['shutdown'], 1, 1)
        listen_thread.join()
        print('Thread joined')
        print('Killing scoreboard')
        for proc in psutil.process_iter():
            if proc.name() == 'scoreboard': proc.terminate()
        print('exiting')
    else:
        listen(display, 6000)
