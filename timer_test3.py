import logging, threading, functools
import time

logging.basicConfig(level=logging.NOTSET,
                    format='%(threadName)s %(message)s')

class PeriodicTimer(object):
    def __init__(self, interval, callback , args=(), single_shot=False):
        self.interval = interval
        self.args = False
        if args:
            #print("args set :%s" % callback.__name__)
            self.args = True
            self.args_list = args
            #print(self.args_list)
        else:
            pass
            #print("args unset :%s" % callback.__name__)

        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            #print(args)
            #print(kwargs)
            callback(*args, **kwargs)
            if not single_shot:
                if self.args:
                    self.thread = threading.Timer(self.interval,
                                              self.callback,self.args_list )
                else:
                    self.thread = threading.Timer(self.interval,
                                              self.callback)

                self.thread.start()


        self.callback = wrapper


    def start(self):
        if self.args:
            self.thread = threading.Timer(self.interval, self.callback, self.args_list)
        else:
            self.thread = threading.Timer(self.interval, self.callback)
        self.thread.start()

    def cancel(self):
        self.thread.cancel()


#####################################################################################

def foo(str):
    logging.info('foo Doing some work...: %s'% str)

def goo(arg):
    logging.info('    goo   Doing some work...: %s' % arg)

def hoo():
    logging.info('           hoo    Doing some work...' )


def mktimer(interval, callback ,*args, **kwargs ):
    t = PeriodicTimer(interval, callback ,args, kwargs )
    return t

#timer1 = PeriodicTimer(1, foo, ("ABABAB",))
#timer2 = PeriodicTimer(1, goo, ("okokok",), single_shot=True)
#timer3 = PeriodicTimer(1, hoo, single_shot=True)
timer1 = mktimer(1, foo, ("ABABAB",))
timer2 = mktimer(1, goo, ("okokok",), True)
timer3 = mktimer(1, hoo, single_shot=True)
timer1.start()
timer2.start()
timer3.start()

