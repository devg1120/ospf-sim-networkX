
#import socket
#import asyncore
#import asynchat
#try:
#    import cPickle as pickle
#except ImportError:
#    import pickle

from thespian.actors import Actor
from thespian.actors import ActorSystem
from thespian.actors import ActorTypeDispatcher
import pprint
from ipaddress import *
from netaddr import IPSet
from netaddr import IPNetwork

import networkx as nx

#from network import Packet

from network import * 
#import term_color as tc
from util import term_color as tc
"""
  tc.green       ("*** this is a test...")                                    
  tc.b_green       ("*** this is a test...")                                  
  tc.u_red         ("*** this is a test...")                                  
  tc.r_green       ("*** this is a test...") 

"""

from util import debug_mode as DEBUG_MODE

_DEBUG_ = DEBUG_MODE.DebugMode()
#_DEBUG_FLAG_LIST =[1,2,3,4]
_DEBUG_FLAG_LIST =[1]
_DEBUG_.make(_DEBUG_FLAG_LIST)

import ospf 
import threading

_terminator = '\0E\0O\0F\0'

#_DEBUG_ = 1 # route table
#_DEBUG_ = 2 # route table
#_DEBUG_A =[2]

#def debug_mode(flag_list):

OSPF_HELLO_SUPERVISON = False
###################################################################

#poll = asyncore.poll
def _poll():
    print("poll...")
    threading.Timer(3, poll).start()

def poll():
    pass
    #print("poll...")

#def mktimer(interval, callback, args=(), single_shot=False):
#    raise NotImplementedError('specify your own function')


def log(msg):
    pass
    #print('log:%s' % msg)

def L(msg):
   pass
   # print('* %s' % (msg))

class Route(object):

    def __init__(self, dest, gateway, netmask, metric, iface):
        self.dest = dest
        self.gateway = gateway
        self.netmask = netmask
        self.metric = metric
        self.iface = iface


class RoutingTable(list):

    def __repr__(self):
        routes = ['Dest\tGateway\tNetmask\tMetric\tInterface']
        for r in self:
            routes.append("%s\t%s\t%s\t%.2f\t%s" % (r.dest, r.gateway, r.netmask, r.metric, r.iface))
        return '\n'.join(routes)

    def clear(self):
        del self[:]

class Iface:
    def __init__(self, name, bandwith, router, address, netmask ):
         self.name = name
         self.bandwith = bandwith
         self.router = router
         self.address = address
         self.netmask = netmask

class  RouteGraph(object):

    class Node:
        def __init__(self, name):
            self.name = name
        def getname(self):
            return self.name

    #class Subnetwork(Node):
    #    def __init__(self, name, *, cost=1):
    #        super().__init__(name)
    #        self.cost = cost
    
    class Subnetwork(Node):
        pass
        #def __init__(self, name, *, cost=1):
        #    super().__init__(name)
    class Router(Node):
        pass
        #def __init__(self, name, *, cost=1):
        #    super().__init__(name)

    def __init__(self, hostname):
        self.hostname = hostname
        self.G = nx.Graph()
        self.subnetworks = {}
        self.routers = {}


    def add_subnetwork(self,name ):
        if not name in self.subnetworks:
            self.subnetworks[name] = self.Subnetwork(name)
            self.G.add_node(self.subnetworks[name])

    def add_router(self,name):
        if not name in self.routers:
            self.routers[name] = self.Router(name)
            self.G.add_node(self.routers[name])


    def get_subnetwork(self,name):
        return self.subnetworks[name]
    def get_router(self,name):
        return self.routers[name]

    def graph_add_edge(self, router, subnetwork, cost):
        self.G.add_edge(self.get_router(router),
                        self.get_subnetwork(subnetwork),
                        weight = cost
                        #eight="cost"
                        )

    def set_networks(self, networks):
        for network, nodes in networks.items():
            _network = self.add_subnetwork(network)
            for router in nodes:
                _router = self.add_router(router)

        for network, nodes in networks.items():
            for router in nodes:
                cost = nodes[router]
                self.graph_add_edge(router, network, cost)

    def dump_networks(self):
        print("------")
        print("[ %s ]" % self.hostname )
        for node in self.G.nodes:
            print(node.name)
        print("------")



    def get_route(self,source, target):
        #print("get_route")
        s = self.get_router(source)
        t = self.get_subnetwork(target)
        try:
            routes_list =  nx.all_shortest_paths(self.G, source=s, target=t)
            for route in routes_list:
               cost = 0
               pre_node = False
               for node in route:
                   if isinstance(node, self.Router):
                       print(node.name + " ", end='')
                   if isinstance(node, self.Subnetwork):
                       print(" ", end='')
                       print(node.name + " ", end='')
                   if pre_node and node:
                       cost += self.G.get_edge_data(pre_node, node)["weight"]  
                   pre_node = node

               print("   cost:%s" % cost)
        except:
            print("Error")

    def dump_shortest_path(self,source ):
        s = self.get_router(source)
        length_dict = nx.shortest_path_length(self.G, source=s)
        #routes_dict = nx.shortest_path(self.G, source=s, weight="cost")
        routes_dict = nx.shortest_path(self.G, source=s )
        for target in routes_dict:
           if isinstance(target, self.Subnetwork):
               print("[%s]" % target.name, end="")
               oldhop = False
               cost = 0
               for hop in routes_dict[target]:
                  if isinstance(hop, self.Router):
                      print(" %s" % hop.name, end="")

                  if oldhop and hop:
                      print(" (%s) " % self.G.get_edge_data(oldhop, hop)["weight"]  , end="")
                      cost += self.G.get_edge_data(oldhop, hop)["weight"]  
                  oldhop = hop
                  
               print(" length=%s cost=%s" % (length_dict[target], cost))

    def get_shortest_path(self,source ):
        path = {}
        s = self.get_router(source)
        length_dict = nx.shortest_path_length(self.G, source=s)
        #routes_dict = nx.shortest_path(self.G, source=s, weight="cost")
        routes_dict = nx.shortest_path(self.G, source=s )
        for target in routes_dict:
           if isinstance(target, self.Subnetwork):
               #print("[%s]" % target.name, end="")
               oldhop = False
               cost = 0
               for hop in routes_dict[target]:
                  if isinstance(hop, self.Router):
                      #print(" %s" % hop.name, end="")
                      pass

                  if oldhop and hop:
                      #print(" (%s) " % self.G.get_edge_data(oldhop, hop)["weight"]  , end="")
                      cost += self.G.get_edge_data(oldhop, hop)["weight"]  
                  oldhop = hop
                  
               #print(" length=%s cost=%s" % (length_dict[target], cost))
               if length_dict[target] == 1:
                   path[target.name] = { "nexthop" : '-',
                                    "length"  : 1, 
                                    "cost"    : cost
                                    }
               else:
                   path[target.name] = { "nexthop" : routes_dict[target][2].name,
                                    "length"  : length_dict[target] , 
                                    "cost"    : cost
                                    }
        return path

    def get_all_shortest_paths(self,source ,target):
        s = self.get_router(source)
        t = self.get_subnetwork(target)
        routes_list = nx.all_shortest_paths(self.G, source=s, target=t) #return list
        for route in routes_list:
           cost = 0
           for node in route:
               if isinstance(node, self.Router):
                   print(node.name + " ", end='')
               if isinstance(node, self.Subnetwork):
                   print(" ", end='')
                   print(node.name + " ", end='')
                   #print(node.cost + " ", end='')
                   #cost += node.cost
           print("   total:%s" % cost)

    def get_dijkstra_path(self,source ,target):
        s = self.get_router(source)
        t = self.get_subnetwork(target)
        routes_list = nx.dijkstra_path(self.G, source=s, target=t) #return list
        for node in routes_list:
               if isinstance(node, self.Router):
                   print(node.name + " ", end='')
               if isinstance(node, self.Subnetwork):
                   print(" ", end='')
                   print(node.name + " ", end='')
                   #print(node.cost + " ", end='')
                   #cost += node.cost

class Router(object):
    class_cnt = 0
    hostname_len = 0

    def __init__(self, hostname, asys, manager_subnet):
        self._asys = asys
        self._manager_subnet = manager_subnet
        self._hostname = hostname
        self._table = RoutingTable()
        self._lsdb = ospf.Database()
        self._interfaces = {}
        self._neighbors = {}
        self._seen = {}
        self._init_timers()
        Router.class_cnt += 1
        print("class_cnt:%s" % self.class_cnt)
        if self.class_cnt == 1:
            Router.hostname_len = len(self._hostname)
        self.instance_cnt = self.class_cnt

    def delete(self):
        self.stop()


    def L1(self, msg):
        if  _DEBUG_.check(1):
            fmt = "%" + str((self.instance_cnt)*(self.hostname_len+1)) + "s" + \
                  "%" + str((self.class_cnt - self.instance_cnt)*(self.hostname_len+1)) +"s" + \
                  "   %s" 
            print(fmt % (self._hostname,"",msg))

    def L2(self, msg):
        if  _DEBUG_.check(2):
            fmt = "%" + str((self.instance_cnt)*(self.hostname_len+1)) + "s" + \
                  "%" + str((self.class_cnt - self.instance_cnt)*(self.hostname_len+1)) +"s" + \
                  "   %s" 
            tc.yellow(fmt % (self._hostname,"",msg))

    def L3(self, msg):
        if  _DEBUG_.check(3):
            fmt = "%" + str((self.instance_cnt)*(self.hostname_len+1)) + "s" + \
                  "%" + str((self.class_cnt - self.instance_cnt)*(self.hostname_len+1)) +"s" + \
                  "   %s" 
            tc.yellow(fmt % (self._hostname,"",msg))

    @staticmethod
    def _get_netadd(addr, netmask):
        addr = addr.split('.')
        netmask = netmask.split('.')
        netadd = []
        for i in range(4):
            netadd.append(str(int(addr[i]) & int(netmask[i])))
        return '.'.join(netadd)

    def _init_timers(self):
        self._dead_timer = None
        self._timers = {}
        self._timers['lsdb'] = mktimer(ospf.AGE_INTERVAL, self._update_lsdb)
        self._timers['refresh_lsa'] = mktimer(ospf.LS_REFRESH_TIME, self._refresh_lsa)
        self._timers['hello'] = mktimer(ospf.HELLO_INTERVAL, self._hello)

    def _update_lsdb(self):
        flushed = self._lsdb.update()
        if flushed:
            log('LSA(s) of %s reached MaxAge and was/were flushed from the LSDB' % (', '.join(flushed), ))

    def _refresh_lsa(self):
        if self._hostname in self._lsdb:
            log('Refreshing own LSA')
            self._advertise()

    def _hello(self):
        """Establish adjacency"""
        #seen = self._seen.keys()  ## pickle
        seen = list(self._seen)
        for iface in self._interfaces.values():
            packet = ospf.HelloPacket(self._hostname, iface.address, iface.netmask, seen)
            iface.transmit(packet)
        for neighbor_id in self._seen:
            if neighbor_id not in self._neighbors:
                self._sync_lsdb(neighbor_id)

    def _update_routing_table(self):   # NEW
        self.L2("_update_routing_table")
        log('Recalculating shortest paths and updating routing table')
        self._table.clear()


        paths = self._lsdb.get_shortest_paths(self._hostname)
        if not paths:
            return
        networks = {}
        for node, lsa in self._lsdb.items():
            for network, data in lsa.networks.items():
                if network not in networks:
                    networks[network] = {}
                networks[network][node] = data[1]

        netmasks = {}
        for node, lsa in self._lsdb.items():
            for network, data in lsa.networks.items():
                netmasks[network] = data[3]

        gateways = {}

        RG = RouteGraph(self._hostname)

        RG.set_networks(networks)
        #RG.dump_networks()

        #print("%s ------------------- get route", self._hostname)
        #RG.get_route(self._hostname, "10.3.2.0")
        #print("%s ------------------- get shortest path" % self._hostname)
        path = RG.get_shortest_path(self._hostname)
        routes = []
        for network in path:
            nexthop = path[network]["nexthop"]
            if nexthop == '-':
                for name  in self._interfaces: 
                    address = self._interfaces[name].address
                    netmask = self._interfaces[name].netmask
                    netadd = self._get_netadd(address, netmask) 
                    if netadd == network: 
                        iface = name
                        gateway = '-'
                        cost = 0
            else:
                #iface, gateway = self._neighbors[nexthop][:2] 
                if nexthop in self._neighbors:
                    iface, gateway = self._neighbors[nexthop][:2] 
                else:
                    iface = '*'
                    gateway = '*'

                cost = path[network]["cost"] 
                netmask = netmasks[network]
                #if network in self._lsdb[nexthop].networks:
                #    netmask = self._lsdb[nexthop].networks[network][3]
                #else:
                #    netmask = '*'

            routes.append({
                            "network" :  network,
                            "netmask" :  netmask,
                            "gateway" :  gateway,
                            "iface"   :  iface,
                            "cost"    :  cost
                })


        #if self._hostname == "RouterA":

        #    print("%s ------------------- get shortest path" % self._hostname)
        #    pp = pprint.PrettyPrinter(indent=4)
        #    pp.pprint(networks )
        #    pp.pprint(self._lsdb)


        for route  in routes:
            #r = Route(network, gateway, netmask, cost, iface)
            r = Route(route["network"], route["gateway"], route["netmask"], route["cost"], route["iface"])
            #if self._hostname == 'RouterA':
            #  self.L1("ADD route: %s %s %s %s" %(  network, netmask ,iface, gateway))
            self._table.append(r) 
        
    #def _update_routing_table2(self):         # OLD
    #    self.L2("_update_routing_table")
    #    log('Recalculating shortest paths and updating routing table')
    #    self._table.clear()
    #    paths = self._lsdb.get_shortest_paths(self._hostname)
    #    if not paths:
    #        return
    #    networks = {}
    #    for node, lsa in self._lsdb.items():
    #        for network, data in lsa.networks.items():
    #            if network not in networks:
    #                networks[network] = {}
    #            networks[network][node] = data[1]
    #    gateways = {}
    #    #if self._hostname == "RouterA":
    #    #        L1(networks)

    #    RG = RouteGraph(self._hostname)
    #    #for network, nodes in networks.items():
    #    #    pp = pprint.PrettyPrinter(indent=4)
    #    #    pp.pprint(nodes)
    #    #    pp.pprint(network)

    #    RG.set_networks(networks)
    #    #RG.dump_networks()

    #    #print("%s ------------------- get route", self._hostname)
    #    #RG.get_route(self._hostname, "10.3.2.0")
    #    #print("%s ------------------- get shortest path" % self._hostname)
    #    path = RG.get_shortest_path(self._hostname)
    #    routes = []
    #    for network in path:
    #        nexthop = path[network]["nexthop"]
    #        if nexthop == '-':
    #            for name  in self._interfaces: 
    #                address = self._interfaces[name].address
    #                netmask = self._interfaces[name].netmask
    #                netadd = self._get_netadd(address, netmask) 
    #                if netadd == network: 
    #                    iface = name
    #                    gateway = '-'
    #                    cost = 0
    #        else:
    #            iface, gateway = self._neighbors[nexthop][:2] 
    #            cost = path[network]["cost"] 
    #            #netmask = self._lsdb[nexthop].networks[network][3]
    #            if network in self._lsdb[nexthop].networks:
    #                netmask = self._lsdb[nexthop].networks[network][3]
    #            else:
    #                netmask = '*'

    #        routes.append({
    #                        "network" :  network,
    #                        "netmask" :  netmask,
    #                        "gateway" :  gateway,
    #                        "iface"   :  iface,
    #                        "cost"    :  cost
    #            })


    #    if self._hostname == "RouterA":

    #        print("%s ------------------- get shortest path" % self._hostname)
    #        pp = pprint.PrettyPrinter(indent=4)
    #        pp.pprint(path)
    #        pp.pprint(self._neighbors )
    #        pp.pprint(routes )
    #        #self._neighbors[next_hop][:2] 
    #        #print("%s ------------------- get all shortest paths" % self._hostname)
    #        #RG.get_all_shortest_paths(self._hostname, "10.3.2.0")


    #    #print("%s ------------------- get dijkstra path" % self._hostname)
    #    #RG.get_dijkstra_path(self._hostname, "10.3.2.0")
    #    """
    #    print("%s ------------------- get shortest path" % self._hostname)
    #    RG.get_dijkstra_path(self._hostname)
    #    print("---")
    #    print("%s ------------------- get all shortest paths" % self._hostname)
    #    RG.get_all_shortest_paths(self._hostname, "10.2.3.0")
    #    print("---")
    #    #RG.get_route("RouterA", "10.2.5.0")
    #    """
    #    pp = pprint.PrettyPrinter(indent=4)
    #    for network, nodes in networks.items():
    #        #if self._hostname == 'RouterA':
    #        #     print("%s : %s => %s" % (self._hostname,network,nodes))
    #        #print("%s %d" % (self._hostname,len(nodes)))
    #        if len(nodes) != 2:
    #            ### GUSA TODO
    #            #print("%s node !=2: %s %s" % (self._hostname,network,nodes))
    #            #gateway = "-"
    #            #netmask ="255.255.255.0"
    #            #
    #            next_hop_list =list(nodes.keys())
    #            next_hop = next_hop_list[0]
    #            dest = next_hop
    #            #print(next_hop)
    #            #print(self._hostname)
    #            if next_hop == self._hostname:
    #                #print("************** continue %s" % network)
    #                for name  in self._interfaces:
    #                    address = self._interfaces[name].address
    #                    netmask = self._interfaces[name].netmask
    #                    netadd = self._get_netadd(address, netmask)
    #                    if netadd == network:
    #                        iface = name
    #                        cost = 0
    #                        gateway = "-"
    #                
    #                r = Route(network, gateway, netmask, cost, iface)
    #                if self._hostname == 'RouterA':
    #                     self.L1("add route: %s %s %s %s" %(  network, netmask ,iface, gateway))
    #                self._table.append(r) 
    #                continue
    #            if next_hop in self._neighbors.keys():    
    #                iface, gateway = self._neighbors[next_hop][:2]
    #                netmask = self._lsdb[dest].networks[network][3]
    #                #
    #                cost = nodes[next_hop]
    #                r = Route(network, gateway, netmask, cost, iface)
    #                if self._hostname == 'RouterA':
    #                     self.L1("add route: %s %s %s %s" %(  network, netmask ,iface, gateway))
    #                self._table.append(r) 
    #            ###
    #            continue
    #        #print("%s node > 1: %s %s" % (self._hostname, network,nodes))
    #        n1, n2 = nodes.keys()
    #        #n = list(nodes.keys())
    #        if self._hostname in nodes:
    #            # The assumption is that the router will prefer sending data
    #            # through its own interface even if the cost is higher
    #            dest = next_hop = (n2 if n1 == self._hostname else n1)
    #            cost = nodes[self._hostname]
    #        else:
    #            # Determine which node is the shorter path to the destination network
    #            dest = (n1 if paths[n1][1] + nodes[n1] < paths[n2][1] + nodes[n2] else n2)
    #            next_hop, cost = paths[dest]
    #            # Get actual cost
    #            cost += nodes[dest]
    #        # Get other info
    #        #iface, gateway = self._neighbors[next_hop][:2]
    #        if next_hop in self._neighbors:
    #            iface, gateway = self._neighbors[next_hop][:2]
    #        else:
    #            continue

    #        #netmask = self._lsdb[dest].networks[network][3]
    #        if dest in self._lsdb:
    #            if network in self._lsdb[dest].networks:
    #                netmask = self._lsdb[dest].networks[network][3]
    #            else:
    #                continue
    #        else:
    #            continue

    #        if self._hostname in nodes:
    #            gateways[cost] = (gateway, iface)
    #            gateway = '-'
    #        #self.L1("add route: %s %s %s %s" %(  network, netmask ,iface, gateway))
    #        r = Route(network, gateway, netmask, cost, iface)
    #        if self._hostname == 'RouterA':
    #            self.L1("add route: %s %s %s %s" %(  network, netmask ,iface, gateway))
    #        self._table.append(r) 

    #    if gateways:
    #        #print("gateways: %s" % gateways)
    #        cost = min(gateways.keys())
    #        gateway, iface = gateways[cost]
    #        self._table.append(Route('0.0.0.0', gateway, '0.0.0.0', cost, iface))

    def _break_adjacency(self, neighbor_id):
        #pass
        # Save reference QObject errors
        if OSPF_HELLO_SUPERVISON:
            self._dead_timer = self._timers[neighbor_id]
            del self._timers[neighbor_id]
        del self._neighbors[neighbor_id]
        del self._seen[neighbor_id]
        log(' '.join([neighbor_id, 'is down']))
        #tc.b_red("%s = > %s is down" % (self._hostname,neighbor_id))
        self._advertise()

    def _flood(self, packet, source_iface=None):
        """Flood received packet to other interfaces"""
        if packet.adv_router == self._hostname:
            log('Flooding own LSA')
        else:
            log('Flooding LSA of %s' % (packet.adv_router, ))
        interfaces = []
        for data in self._neighbors.values():
            interfaces.append(data[0])
        if source_iface in interfaces:
            interfaces.remove(source_iface)
        for iface_name in interfaces:
            iface = self._interfaces[iface_name]
            iface.transmit(packet)

    def _advertise(self):
        networks = {}
        for neighbor_id, data in self._neighbors.items():
            iface_name, address, netmask = data
            iface = self._interfaces[iface_name]
            cost = ospf.BANDWIDTH_BASE / float(iface.bandwidth)
            netadd = self._get_netadd(address, netmask)
            networks[netadd] = (neighbor_id, cost, address, netmask)

        ### GUSA TODO
        for name  in self._interfaces:
            #if name != "eth0":
            #   continue
            if self._interfaces[name].neighbor_connect:
               continue
            #print(name)
            #print(self._interfaces[name].address)
            #print(self._interfaces[name].netmask)
            address = self._interfaces[name].address
            netmask = self._interfaces[name].netmask
            #cost = 100
            cost = ospf.BANDWIDTH_BASE / float( self._interfaces[name].bandwidth)
            netadd = self._get_netadd(address, netmask)
            neighbor_id = self._hostname
            #neighbor_id = "-"
            networks[netadd] = (neighbor_id, cost, address, netmask)
        ###

        # Create new or update existing LSA
        if self._hostname in self._lsdb:
            lsa = self._lsdb[self._hostname]
            lsa.seq_no += 1
            lsa.age = 1
            lsa.networks = networks
        else:
            lsa = ospf.LinkStatePacket(self._hostname, 1, 1, networks)
        self._lsdb.insert(lsa)
        # Flood LSA to neighbors
        self._flood(lsa)
        self._update_routing_table()
        #
        #self.show_table()

    def _sync_lsdb(self, neighbor_id):
        topology_changed = (neighbor_id not in self._neighbors)
        if topology_changed:
            log('Adjacency established with %s' % (neighbor_id, ))
            #print("%s:self._neighbors:%s" % (self._hostname,self._neighbors))
            #tc.b_red("%s topology_changed neighbor_id:%s" % (self._hostname,neighbor_id))
        self._neighbors[neighbor_id] = self._seen[neighbor_id]
        #print(">> %s:self._neighbors:%s" % (self._hostname,self._neighbors))
        if self._hostname not in self._lsdb:
            log('Creating initial LSA')
            self._advertise()
        elif topology_changed:
            self._advertise()
            # Sync LSDB with neighbor
            iface_name = self._neighbors[neighbor_id][0]
            iface = self._interfaces[iface_name]
            for lsa in self._lsdb.values():
                iface.transmit(lsa)

    def iface_create(self, name, bandwidth ):
        if name not in self._interfaces:
            self._interfaces[name] = Interface(self._asys, self._manager_subnet, name, bandwidth,  self)

    def iface_config(self, name, address, netmask ):
        iface = self._interfaces[name]

        iface.address = address
        iface.netmask = netmask
        iface.setNIC()

    """  route table element
            self.dest = dest
            self.gateway = gateway
            self.netmask = netmask
            self.metric = metric
            self.iface = iface
    """        
    def show_table(self):
        #L("%s:" % self._hostname)
        self.L1("neighbors")
        for nb in self._neighbors:
            self.L1("%s => %s %s" % (self._hostname,nb,self._neighbors[nb]))
        #print(self._neighbors)
        #self._update_routing_table()
        self.L1("routetable")
        for r in self._table:
            self.L1("%-14s %14s %10s %6s %s" %  (r.dest, r.netmask, r.metric, r.iface, r.gateway))

    def route_found(self, dest_ip):
        for r in self._table:
            network = self._get_netadd(dest_ip, r.netmask)
            if network == r.dest:
                return { "iface" : r.iface,
                         "nexthop" : r.gateway }

    def start(self):
        # Start timers
        for t in self._timers.values():
            t.start()
        self._hello()

    def stop(self):
        for t in self._timers.values():
            #t.stop()
            t.cancel()
        for iface in self._interfaces.values():
            iface.handle_close()

    def ishostip(self,ip):
        for name in self._interfaces:
            iface = self._interfaces[name]
            if iface.address == ip:
                return True
        return False

    def ICMP(self, packet):
        if packet.payload["reply"] == False:
            packet.dest_ip = packet.source_ip
            packet.payload["reply"] = True
            print("%s ICMP REPLY from %s" % (self._hostname, packet.source_ip))
            self.send(packet)
        else:
            print("%s ICMP COMP from %s" % (self._hostname,  packet.source_ip))

    def protocol_dispatch(self, packet):
        if packet.protocol == Protocol.TEST:
            print("%s PROTOCOL TEST TERMINATE from %s" % (self._hostname, packet.source_ip))
        elif packet.protocol == Protocol.ICMP:
            #print("%s PROTOCOL ICMP TERMINATE from %s" % (self._hostname, packet.source_ip))
            self.ICMP(packet)
        else:
            print("%s protocol Error from %s" % (self._hostname, packet.source_ip))

    def recv(self, packet):
        #print("%s user paclet recive" % self._hostname)
        #print(packet.dest_ip)
        if self.ishostip(packet.dest_ip):
            #print("%s user paclet terminate" % self._hostname)
            self.protocol_dispatch( packet) 
        else:
            #print("%s user paclet routine" % self._hostname)
            self.routing(packet)

    #def send(self, packet):
    #    route = self.route_found(packet["dest_ip"])
    #    if route["nexthop"] == '-':
    #        self._interfaces[route["iface"]].send(packet["dest_ip"], packet)
    #    else:
    #        self._interfaces[route["iface"]].send(route["nexthop"], packet)

    def send(self, packet):
        route = self.route_found(packet.dest_ip)
        packet.source_ip = self._interfaces[route["iface"]].address  
        if route["nexthop"] == '-':
            self._interfaces[route["iface"]].send(packet.dest_ip, packet)
        else:
            self._interfaces[route["iface"]].send(route["nexthop"], packet)

    def routing(self, packet):
        route = self.route_found(packet.dest_ip)
        if route["nexthop"] == '-':
            self._interfaces[route["iface"]].send(packet.dest_ip, packet)
        else:
            self._interfaces[route["iface"]].send(route["nexthop"], packet)

    def testsend(self, dest_ip):
        #packet = {
        #        "dest_ip": dest_ip,
        #        "payload": "TEST"
        #        }
        packet = IPpacket(Protocol.TEST,dest_ip)
        packet.set_payload({"body": "TEST"})
        self.send(packet)

    def icmp(self, dest_ip):
        packet = IPpacket(Protocol.ICMP,dest_ip)
        packet.set_payload({"reply": False})
        self.send(packet)

#class Interface(asyncore.dispatcher):
class Interface():
    """Physical Router interface"""
    def __init__(self, asys, manager_subnet, name, bandwidth,router ):
        self._asys = asys
        self._manager_subnet = manager_subnet
        self.name = name
        self.bandwidth = bandwidth
        self.router = router
        self.neighbor_connect = False
        log('%s up' % (self.name, ))

    def setNIC(self):
        log("setting NIC")

        #self._asys.ask(iface, iface_data)
        self.NIC = self._asys.createActor(NIC);
        nicinfo = NICinfo(self._asys,
                          self._manager_subnet,
                          self.address,
                          self.netmask,
                          self)

        self._asys.ask(self.NIC, nicinfo)

    @staticmethod
    def writable():
        return False

    def handle_close(self):
        pass
        #self.close()
        #for conn in self.connections.values():
        #    conn.handle_close()
        #log('%s down' % (self.name, ))

    def handle_accept(self):
        pass
        #conn, addr = self.accept()
        # Dispatch connection to a IfaceRx
        #IfaceRx(self.router, self.name, self.connections, conn)

    def recieve(self,packet):
        #log("iface  packet recieve")
        if isinstance(packet, ospf.HelloPacket):
             self.neighbor_connect = True
             neighbor_id = packet.router_id
             log('Seen %s' % (neighbor_id, ))
             #self.router.L3('%s' % (neighbor_id, ))
             # Reset Dead timer
             if OSPF_HELLO_SUPERVISON:
                 if neighbor_id in self.router._timers:
                     self.router._timers[neighbor_id].stop()
                 #t = mktimer(ospf.DEAD_INTERVAL, self.router._break_adjacency, (neighbor_id, ), single_shot=True)
                 t = mktimer(ospf.DEAD_INTERVAL, self.router._break_adjacency, neighbor_id , single_shot=True)
                 t.start()
                 self.router._timers[neighbor_id] = t
             self.router._seen[neighbor_id] = (self.name, packet.address, packet.netmask)
             if self.router._hostname in packet.seen:
                 self.router._sync_lsdb(neighbor_id)
        elif isinstance(packet, ospf.LinkStatePacket):
             # Insert to Link State database
             if self.router._lsdb.insert(packet):
                 if packet.adv_router == self.router._hostname:
                     self.router._advertise()
                 else:
                     log('Received LSA of %s via %s and merged to the LSDB' % (packet.adv_router, self.name))
                     self.router._flood(packet, self.name)
                     self.router._update_routing_table()
             elif packet.adv_router == self.router._hostname and packet.seq_no == 1:
                 self.router._advertise()

        else: # USER PACKET
             self.router.recv(packet)


    def transmit(self, packet):
        """Transmit a packet through the interface"""
        send_packet = TransferFrame("mc","--","dest","source",packet)
        self._asys.ask(self.NIC, send_packet)
        
    def send(self, nexthop,packet):
        """Transmit a packet through the interface"""
        #packet.source_ip = self.address 
        send_packet = TransferFrame("uc","--",nexthop,"source",packet)
        self._asys.ask(self.NIC, send_packet)



