
import os
import sys
import signal
#import socket
import time
import threading ,functools
from enum import Enum
#import ConfigParser
from thespian.actors import Actor
from thespian.actors import ActorSystem
from thespian.actors import ActorTypeDispatcher
import pprint
from netaddr import IPNetwork
#from PyQt4 import QtCore, QtGui, uic

import router
import ospf

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

    def stop(self):
        self.thread.cancel()


##############################################################################
def mktimer(interval, callback ,*args, **kwargs ):
    t = PeriodicTimer(interval, callback ,args, kwargs )
    return t

##############################################################################
class Singleton(object):
    def __new__(cls, *args, **kargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance

class RouterManager(Singleton):
    def __init__(self):
        self.router_list = []

    def regist(self,router):
        self.router_list.append(router)

    def get(self):
        return self.router_list

    def poll(self):
        # print("router manager polling...")
        for router in self.router_list:
            #print("%s" % router._hostname)
            router.show_table()

    def make(self,flag_list):
        _debug_bit = 0b000000
        for flag in flag_list:
            tmp = 1<<(flag -1)
            _debug_bit = _debug_bit | tmp
        self._DEBUG_ = _debug_bit
        #print("_DEBUG_%s:" % bin(self._DEBUG_))
    
    def check(self,flag):
        #print("debug_mode_check:%s" % str(flag))
        cbit = 1<<(flag-1)
        #print(bin(self._DEBUG_))
        #print(bin(cbit))
        result = self._DEBUG_ & cbit 
        #print(result)
        if result > 0:
            return True
        else:
            return False

##############################################################################
def poll():
    print("poll...")


class Protocol(Enum):
    TEST = 1
    ICMP = 2

#class Packet:
class IPpacket:
    def __init__(self, protocol, dest_ip, ):
        self.protocol = protocol
        self.dest_ip = dest_ip
        self.source_ip = ""
        self.payload = {}
    def set_source_ip(self, source_ip):
        self.source_ip = source_ip

    def set_payload(self, payload):
        self.payload = payload

class TransferFrame:
    def __init__(self, t_type,  p_type , dest_ip, source_ip, packet):
         self.t_type = t_type
         self.p_type = p_type
         self.dest_ip = dest_ip
         self.source_ip = source_ip
         self.packet = packet

class NICinfo:
    def __init__(self, asys, manager_subnet, address, netmask, iface  ):
         self._asys = asys
         self._manager_subnet = manager_subnet
         self._address = address
         self._netmask = netmask
         self._iface   = iface

class NIC(ActorTypeDispatcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def receiveMsg_NICinfo(self, info, sender):
        #self.iface = info.iface
        #self.subnet_actor = info.subnet_actor
        self._asys = info._asys
        self._manager_subnet =info._manager_subnet
        self._address =info._address
        self._netmask =info._netmask
        self._iface =info._iface

        ip = IPNetwork(self._address + "/" + self._netmask)
        ipaddr = str(ip.ip)
        subnet_strname = str(ip.network) + "/"+ str(ip.prefixlen)
        router.log("subnet: %s" % subnet_strname)
        self.subnet_actor_addr = self._manager_subnet.get_actor_addr(subnet_strname)
        router.log("subnet actor addr:%s" % self.subnet_actor_addr)

        node = Node(ipaddr,self.myAddress)
        self._asys.ask(self.subnet_actor_addr, node)

    #def receiveMsg_Packet(self, packet, sender):
    def receiveMsg_TransferFrame(self, packet, sender):
        #print("receive packet __ sender:%s" % sender)
        #print("subnet:%s" % self.subnet_actor_addr)
        if self.subnet_actor_addr == sender:
            # recive packet
            router.log("from network: %s => %s" % (packet.source_ip, self._address))
            self._iface.recieve(packet.packet)
        else:
            # send rquest packet
            #print("from self: %s" % self._address)
            packet.source_ip = self._address
            self._asys.ask(self.subnet_actor_addr, packet)

#        if isinstance(packet.packet, ospf.HelloPacket):
#            print("     HelloPacket")
#        if isinstance(packet.packet, ospf.LinkStatePacket):
#            print("     LinkStatePacket")

    #def receiveMessage(self, message, sender):
#    def receiveMessage(self, packet, sender):
#        print("receive packet")
#        if isinstance(packet, ospf.HelloPacket):
#            print("     HelloPacket")
#        if isinstance(packet, ospf.LinkStatePacket):
#            print("     LinkStatePacket")



class Node:
    def __init__(self, ip, actor_addr):
         self.ip = ip
         self.actor_addr = actor_addr
         #print(self.table)

class SubNetwork(ActorTypeDispatcher):
    def __init__(self, *args, **kwargs ):
        super().__init__(*args, **kwargs)
        self.hostname = ""
        self.interface = []
        self.route_table = []
        self.node_dic = {}

    def receiveMsg_RouteTable(self, table, sender):
         if msg == "name":
             self.send(sender, self.globalName)
         self.hostname = table.table["hostname"]
         self.interface = table.table["interface"]
         self.route_table = table.table["route"]

    def receiveMsg_Node(self, node, sender):
         #print("subnet[%s] add node %s" % (self.globalName,node.ip))
         #self.node_dic[node.ip] = sender
         self.node_dic[node.ip] = node.actor_addr

    def receiveMsg_Ping(self, ping, sender):
         #print("           subnet[%s] ping next: %s" % (self.globalName,ping.next_hop))
         # next forword
         #print(ping.next_hop)
         _ping = asys.ask(self.node_dic[ping.next_hop], ping)
         self.send(sender, _ping)

    #def receiveMsg_Packet(self, packet, sender):
    def receiveMsg_TransferFrame(self, packet, sender):
        #print("subnet packet receive")
        if packet.t_type == "mc":
           for node_ip in self.node_dic:
                if node_ip != packet.source_ip:
                    #print("source_ip unmatch:%s" % node_ip)
                    #self.asys.ask(self.node_dic[node_ip],packet)
                    self.send(self.node_dic[node_ip],packet)
        elif packet.t_type == "uc":
            if packet.dest_ip in self.node_dic:
                self.send(self.node_dic[packet.dest_ip],packet)
            else:
                raise Exception("%s not reach :%s" % (self.globalName, packet.dest_ip))
            

    def receiveMsg_str(self, msg, sender):
         if msg == "name":
             self.send(sender, self.globalName)
         elif msg == "node-dump":
             self.dump()
         elif msg == "table-get":
             self.send(sender, self.route_table)

    def dump(self):
         #print("---------------------------")
         #print(self.globalName)
         #print("#node list")
         for key in self.node_dic:
             pass
             #print("   %s" % key)
         #print("---------------------------")


class Manager_SubNetwork(Singleton):
    def __init__(self, asys):
        self.asys = asys
        self.netaddress_dic = {}

    def create(self,s_netaddress):
        subnetwork = self.asys.createActor(SubNetwork,  globalName = s_netaddress);
        self.netaddress_dic[s_netaddress] = subnetwork
        #self.ask(subnetwork, self.asys)
        return subnetwork

    def get_actor_addr(self, subnet):
        for key in self.netaddress_dic:
            if key == subnet:
               return self.netaddress_dic[key]

    def dump(self):
        for key in self.netaddress_dic:
            self.asys.ask(self.howetaddress_dic[key], "node-dump")
