import logging, threading, functools
import time

logging.basicConfig(level=logging.NOTSET,
                    format='%(threadName)s %(message)s')

class PeriodicTimer(object):
    def __init__(self, interval, callback):
        self.interval = interval

        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            result = callback(*args, **kwargs)
            if result:
                self.thread = threading.Timer(self.interval,
                                              self.callback)
                self.thread.start()

        self.callback = wrapper

    def start(self):
        self.thread = threading.Timer(self.interval, self.callback)
        self.thread.start()

    def cancel(self):
        self.thread.cancel()


def foo():
    logging.info('Doing some work...')
    return True

def goo():
    logging.info('       Doing some work...')
    return True

timer = PeriodicTimer(1, foo)
timer2 = PeriodicTimer(2, goo)
timer.start()
timer2.start()

