import os
import time
import traceback
import sys
from thespian.actors import ActorSystem
from thespian.actors import Actor
from thespian.actors import ActorTypeDispatcher
from thespian.troupe import troupe
from datetime import timedelta

"""

Parent will send and will also expect to receive
50k messages per child.

[PARENT] ---- [CHILD 1] -> [PARENT]
         |--- [CHILD 2] ---^
         |--- [CHILD 3] ---^
         |--- [CHILD 4] ---^
         |--- [CHILD 5] ---^

"""


class ParentProcessor(ActorTypeDispatcher):

    def __init__(self):
        Actor.__init__(self)
        self.total = 0

    def receiveMsg_int(self, msg, sender):
        """Spawn up 5 Children workers
           Expecting 50k messages back to the parent from each child
        """

        print("starting here")
        try:

            for i in range(5):
                child = self.createActor(ChildProcessor)
                self.send(child, i)
             # print("total count: %s" % self.total_count)

        except:
            traceback.print_exc(file=sys.stdout)

    def receiveMsg_str(self, msg, sender):

        # Printing to show the delay after the first 5 return
        # First 5 is a message from each child that was spawn
        # This is what is returned before the long pause:
        #
        # starting here
        # 0: 0
        # 1: 0
        # 2: 0
        # 3: 0
        # 4: 0
        # <long pause here>
        print(msg)


class ChildProcessor(ActorTypeDispatcher):
    """Actor that processes mdns"""

    def receiveMsg_int(self, msg, sender):
        """send back n work for each each parent"""
        try:
            for i in range(50000):
                self.send(sender, "%s: %s" % (msg, i))

        except:
            traceback.print_exc()


def main():

    max_wait = timedelta(seconds=10)

    #system = ActorSystem('multiprocTCPBase')
    system = ActorSystem()

    parent = system.createActor(ParentProcessor)
    system.tell(parent, 1)

    print(system.listen(max_wait))


if __name__ == "__main__":
    START = time.time()
    main()
    print("Time taken: %ss" % str(time.time() - START))
