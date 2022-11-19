
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
                display.canvas.court = msg[1]
                conn.send('ack')
            if msg[0] == 'logo':
                display.canvas.load_logo(msg[1])
                conn.send('ack')
            if msg[0] == 'mesg':
                display.show_message(msg[1:5])
                conn.send('ack')
            if msg[0] == 'shutdown':
                print('Shutting down display listener')
                running = False
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
        conn = Connection('localhost', config.display.getint("port", 6000))
        conn.send(['shutdown'], 1, 1)
        listen_thread.join()
        print('Thread joined')
        print('Killing scoreboard')
        for proc in psutil.process_iter():
            if proc.name() == 'scoreboard': proc.terminate()
        print('exiting')
    else:
        from systemd.daemon import notify, Notification
        notify(Notification.READY)
        listen(display, 6000)
