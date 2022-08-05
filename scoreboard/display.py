
from multiprocessing.connection import Listener
from scoreboard import Config
from threading import Thread



def listen(disp, port):
    display = disp
    listener = Listener(('0.0.0.0', port), authkey=b'vbscores')
    running = True
    while running:
        conn = listener.accept()

        try:
            msg = conn.recv()
            if msg[0] == 'clock':
                display.update_clock()
                conn.send('ack')
            if msg[0] == 'match':
                display.update_match(msg[1])
                conn.send('ack')
            if msg[0] == 'next_match':
                display.update_next_match(msg[1], msg[2])
                conn.send('ack')
            if msg[0] == 'timer':
                display.show_timer(msg[1], msg[2])
                conn.send('ack')
            if msg[0] == 'court':
                display.court = msg[1]
                conn.send('ack')
            if msg[0] == 'logo':
                display.load_logo(msg[1])
                conn.send('ack')
            if msg[0] == 'mesg':
                display.show_message(msg[1:4])
                conn.send('ack')
            if msg[0] == 'shutdown':
                print('Shutting down display listener')
                running = False
        except Exception as e:
            print(f'QT Display Exception: [{type(e).__name__}] - {e}')
        finally:
            conn.close()

    listener.close()



def rgb_display(config_file=None):
    config = Config(config_file)
    config.read()

    cols = config.display.getint("cols") * config.display.getint("chain_length", 1)

    if config_file:
        from scoreboard.canvas_qt import Canvas
    elif cols == 192:
        from scoreboard.canvas_192x64 import Canvas
    else:
        from scoreboard.canvas_96x32 import Canvas
    display = Canvas(config)

    if config_file:
        listen_thread = Thread(target=listen, args=(display,config.display.getint("port", 6000)))
        listen_thread.start()

        display.win.show()
        display.exec_()

        print('Qt Display closed. Waiting for listen thread to exit.')
        listen_thread.join()
        print('Thread joined')
    else:
        listen(display, 6000)
