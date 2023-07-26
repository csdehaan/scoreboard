
from datetime import datetime
from datetime import timedelta
import threading


def periodic_task(interval, iterations = 1000000000, cleanup = None):
    def outer_wrap(function):
        def wrap(*args, **kwargs):
            stop = threading.Event()
            def inner_wrap():
                iteration = 0
                delta = timedelta(seconds=interval)
                start_time = datetime.now()
                while iteration < iterations and not stop.isSet():
                    function(iteration, *args, **kwargs)
                    iteration += 1
                    stop.wait((start_time + (delta * iteration) - datetime.now()).total_seconds())

                if cleanup:
                    cleanup(*args, **kwargs)

            t = threading.Timer(0, inner_wrap)
            t.daemon = True
            t.start()
            return stop
        return wrap
    return outer_wrap