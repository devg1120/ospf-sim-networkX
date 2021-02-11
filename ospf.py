# -*- coding: utf-8 -*-
# Copyright (c) 2009 Darwin M. Bautista
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import dijkstra

from util import term_color as tc
"""
 # term_color :usage
  tc.green         ("*** this is a test...")                                    
  tc.b_green       ("*** this is a test...")                                  
  tc.u_red         ("*** this is a test...")                                  
  tc.r_green       ("*** this is a test...") 

"""

from util import debug_mode as DEBUG_MODE

_DEBUG_ = DEBUG_MODE.DebugMode()


#TIME_SCALE = 20 # 1 minute (60 seconds) is to 3 seconds (60 / 3 = 20)
TIME_SCALE = 200 # 1 minute (60 seconds) is to 3 seconds (60 / 3 = 20)


def _scale_time(minutes):
    return (60.0 * minutes / TIME_SCALE)


BANDWIDTH_BASE = 100000000 # 100 Mbps
#HELLO_INTERVAL = 10 # 10 seconds
HELLO_INTERVAL = 4 # 10 seconds
#DEAD_INTERVAL = 4 * HELLO_INTERVAL # typical value is 4 times the HELLO_INTERVAL
DEAD_INTERVAL = 10 * HELLO_INTERVAL # typical value is 4 times the HELLO_INTERVAL
AGE_INTERVAL = _scale_time(1) # 1 minute
LS_REFRESH_TIME = _scale_time(30) # 30 minutes
MAX_AGE = _scale_time(60) # 1 hour


class LinkStatePacket(object):

    def __init__(self, router_id, age, seq_no, networks):
        self.adv_router = router_id
        self.age = age
        self.seq_no = seq_no
        self.networks = networks

    def __repr__(self):
        stat = '\nADV Router: %s\nAge: %d\nSeq No.: %d\nNetworks: %s\n\n' % (self.adv_router, self.age, self.seq_no, self.networks)
        return stat


class HelloPacket(object):

    def __init__(self, router_id, address, netmask, seen):
        self.router_id = router_id
        self.address = address
        self.netmask = netmask
        self.seen = seen


class Database(dict):

    def lsadiff(self,lsa):
         if lsa.adv_router in self:
             #print("%10s  EXIST" % (lsa.adv_router))
             db_lsa = self[lsa.adv_router]
             #print("  router:%10s  %s" % (db_lsa.adv_router,lsa.adv_router))
             #print("  age:%10s  %s" % (db_lsa.age,       lsa.age))
             #print("  seq_no:%10s  %s" % (db_lsa.seq_no,    lsa.seq_no))
             #print("  networks:%s  %s" % (db_lsa.networks,   lsa.networks))
             if db_lsa.networks != lsa.networks:
                 pass
                  #tc.b_red("networks update")
         else:
             pass
             # print("%10s  NEW" % (lsa.adv_router))

    def insert2(self, lsa):
        """Returns True if LSA was added/updated"""
        #self.lsadiff(lsa)
        if lsa.adv_router not in self or \
           lsa.seq_no > self[lsa.adv_router].seq_no:
            self[lsa.adv_router] = lsa
            #tc.red("ospf db lsa update:%s" % lsa.adv_router)
            return True
        else:
            return False

    def insert(self, lsa):
        """Returns True if LSA was added/updated"""
        #self.lsadiff(lsa)
        if lsa.adv_router not in self or \
           lsa.networks != self[lsa.adv_router].networks:
           #lsa.seq_no > self[lsa.adv_router].seq_no:
            self[lsa.adv_router] = lsa
            #tc.red("ospf db lsa update:%s" % lsa.adv_router)
            return True
        else:
            return False

    def remove(self, router_id):
        """Remove LSA from router_id"""
        #tc.b_red("remove:%s" % router_id)
        if router_id in self:
            del self[router_id]

    def flush(self):
        """Flush old entries"""
        flushed = []
        for router_id in self:
            if self[router_id].age > MAX_AGE:
                flushed.append(router_id)
        map(self.pop, flushed)
        return flushed

    def update(self):
        """Update LSDB by aging the LSAs and flushing expired LSAs"""
        for adv_router in self:
            self[adv_router].age += 1
        return self.flush()

    def get_shortest_paths(self, router_id):
        """Return a list of shortest paths from router_id to all other nodes"""
        g = dijkstra.Graph()
        nodes = []
        paths = {}
        for lsa in self.values():
            nodes.append(lsa.adv_router)
            for data in lsa.networks.values():
                neighbor_id, cost = data[:2]
                g.add_e(lsa.adv_router, neighbor_id, cost)
        if router_id in nodes:
            nodes.remove(router_id)
        # Find a shortest path from router_id to dest
        dist, prev = g.s_path(router_id)
        for dest in nodes:
            # Trace the path back using the prev array.
            path = []
            current = dest
            while current in prev:
                path.insert(0, prev[current])
                current = prev[current]
            try:
                cost = dist[dest]
            except KeyError:
                continue
            else:
                next_hop = (path[1] if len(path) > 1 else dest)
                paths[dest] = (next_hop, cost)
        return paths
