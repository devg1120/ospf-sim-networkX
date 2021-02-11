
import os
import sys
import signal
#import socket
import time
import threading ,functools
#import ConfigParser
from thespian.actors import Actor
from thespian.actors import ActorSystem
from thespian.actors import ActorTypeDispatcher
import pprint
#from PyQt4 import QtCore, QtGui, uic

import router
from network import *

"""
# topology


|-----------[RouterA]-----------------[RouterB]----------|
        eth0   |     eth1         eth1    |     eth0
 10.2.1.0/24   |        10.2.2.0/24       |     10.2.3.0/24
          .1   |      .1          .254    |     .1
               |                          |
               |eth2                      |eth2
               |10.3.1.0/24               |10.3.2.0/24
               |.1                        |.1
               |                          |
               |                          |
               |    eth1         eth2     |
               |    .254         .254     |
               +--------[RouterC]---------+
                            |      
                            |eth0
                            |.1
                   |--------+-------|
                       10.2.4.0/24





# route table

RouterA:
neighbors
RouterA => RouterC ('eth2', '10.3.1.254', '255.255.255.0')
RouterA => RouterB ('eth1', '10.2.2.254', '255.255.255.0')
routetable
10.3.1.0        255.255.255.0   100000.0   eth2 -
10.2.2.0        255.255.255.0   100000.0   eth1 -
10.3.2.0        255.255.255.0   200000.0   eth1 10.2.2.254
10.2.4.0        255.255.255.0   100000.0   eth2 10.3.1.254
10.2.3.0        255.255.255.0   100000.0   eth1 10.2.2.254
10.2.1.0        255.255.255.0          0   eth0 -
0.0.0.0               0.0.0.0   100000.0   eth1 10.2.2.254


RouterB:
neighbors
RouterB => RouterC ('eth2', '10.3.2.254', '255.255.255.0')
RouterB => RouterA ('eth1', '10.2.2.1', '255.255.255.0')
routetable
10.2.2.0        255.255.255.0   100000.0   eth1 -
10.2.4.0        255.255.255.0   100000.0   eth2 10.3.2.254
10.2.3.0        255.255.255.0          0   eth0 -
10.3.1.0        255.255.255.0   200000.0   eth1 10.2.2.1
10.3.2.0        255.255.255.0   100000.0   eth2 -
10.2.1.0        255.255.255.0   100000.0   eth1 10.2.2.1
0.0.0.0               0.0.0.0   100000.0   eth2 10.3.2.254


RouterC:
neighbors
RouterC => RouterA ('eth1', '10.3.1.1', '255.255.255.0')
RouterC => RouterB ('eth2', '10.3.2.1', '255.255.255.0')
routetable
10.3.1.0        255.255.255.0          0   eth1 -
10.2.2.0        255.255.255.0   200000.0   eth2 10.3.2.1
10.3.2.0        255.255.255.0   100000.0   eth2 -
10.2.4.0        255.255.255.0          0   eth0 -
10.2.3.0        255.255.255.0   100000.0   eth2 10.3.2.1
10.2.1.0        255.255.255.0   100000.0   eth1 10.3.1.1
0.0.0.0               0.0.0.0   100000.0   eth2 10.3.2.1


"""



if __name__ == '__main__':

    # Override default functions
    #router.mktimer = mktimer
    rm = RouterManager() 
    #router.log = log
    asys = ActorSystem()
    manager_subnet = Manager_SubNetwork(asys)
    
    subnet1 = manager_subnet.create("10.2.1.0/24")
    subnet2 = manager_subnet.create("10.2.2.0/24")
    subnet3 = manager_subnet.create("10.2.3.0/24")
    subnet4 = manager_subnet.create("10.2.4.0/24")
    subnet5 = manager_subnet.create("10.3.1.0/24")
    subnet6 = manager_subnet.create("10.3.2.0/24")
    
    print(asys.ask(subnet1, "name"))
    print(asys.ask(subnet2, "name"))
    print(asys.ask(subnet3, "name"))
    print(asys.ask(subnet4, "name"))
    print(asys.ask(subnet5, "name"))
    print(asys.ask(subnet6, "name"))

    RA = router.Router("RouterA", asys, manager_subnet)
    RA.iface_create("eth0", 1000)
    RA.iface_config("eth0", "10.2.1.1", "255.255.255.0")
    RA.iface_create("eth1", 10)
    RA.iface_config("eth1", "10.2.2.1", "255.255.255.0")
    RA.iface_create("eth2", 1000)
    RA.iface_config("eth2", "10.3.1.1", "255.255.255.0")


    RB = router.Router("RouterB", asys, manager_subnet)
    RB.iface_create("eth0", 1000)
    RB.iface_config("eth0", "10.2.3.1", "255.255.255.0")
    RB.iface_create("eth1", 1000)
    RB.iface_config("eth1", "10.2.2.254", "255.255.255.0")
    RB.iface_create("eth2", 1000)
    RB.iface_config("eth2", "10.3.2.1", "255.255.255.0")


    RC = router.Router("RouterC", asys, manager_subnet)
    RC.iface_create("eth0", 1000)
    RC.iface_config("eth0", "10.2.4.1", "255.255.255.0")
    RC.iface_create("eth1", 1000)
    RC.iface_config("eth1", "10.3.1.254", "255.255.255.0")
    RC.iface_create("eth2", 1000)
    RC.iface_config("eth2", "10.3.2.254", "255.255.255.0")


    #router_timer = PeriodicTimer(10, router.poll)
    #router_timer = PeriodicTimer(10, poll)

    router_timer = PeriodicTimer(5, rm.poll) 
    router_timer.start()

    rm.regist(RA) 
    rm.regist(RB) 
    rm.regist(RC) 

    RA.start()
    RB.start()
    RC.start()


    #time.sleep(2)
    #manager_subnet.dump()
    #RA.show_table()

    #time.sleep(100000)

    sys.exit()
