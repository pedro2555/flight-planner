#!/bin/bash/python3

import csv
from collections import defaultdict
import geopy.distance

class Node(object):
    def __init__(
            self,
            name,
            lat,
            lon,
            parent=None,
            cost=0.0,
            g_cost=0.0,
            via='DCT'):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.parent = parent
        self.cost = cost # cost from parent node
        self.g_cost = g_cost # distance from starting node
        self.h_cost = 0.0 # distance to goal
        self.via = via

    @property
    def f_cost(self):
        return self.g_cost + self.h_cost

    @property
    def key(self):
        return ','.join([
                'S',
                self.name,
                '{:.5f}'.format(self.lat),
                '{:.5f}'.format(self.lon)])

    def long_route(self):
        if not self.parent:
            return self.name
        return ' '.join([self.parent.long_route(), self.via, self.name])

    def short_route(self, via=None):
        if not self.parent:
            return self.name

        if not via or via != self.via:
            return ' '.join([self.parent.short_route(via=self.via),
                                                     self.via,
                                                     self.name])
        return self.parent.short_route(via=self.via)

    def distance_to(self, node):
        return geopy.distance.vincenty(
                (self.lat, self.lon),
                (node.lat, node.lon)
            ).nm

    @property
    def neighbours(self):
        result = set()
        for neighbour in ATS[self.key]:
            neighbour.g_cost = neighbour.cost + self.g_cost
            neighbour.parent = self
            result.add(neighbour)
        return result

ATS = defaultdict(list)
with open('ats.txt') as f:
    reader = csv.reader(f, delimiter=',')
    for line in reader:
        if len(line) == 0:
            continue
        t = line[0]
        if t == 'A':
            _, airway, _ = line
        elif t == 'S':
            _, name, lat, lon, nname, nlat, nlon, _, _, ncost = line
            parent = Node(name, float(lat), float(lon))
            node = Node(
                    nname,
                    float(nlat),
                    float(nlon),
                    cost=float(ncost),
                    via=airway)
            ATS[parent.key].append(node)

def route(start, end):
    print('finding route from %s to %s' % (start.name, end.name))
    visited = set()
    queue = [(start),]
    current = None

    while not current or current.key != end.key:
        queue = sorted(queue, key=lambda x: x.f_cost)
        current = queue.pop(0)

        # pass only once per WPT
        if current.key in visited:
            continue
        visited.add(current.key)

        for n in current.neighbours:
            n.h_cost = n.distance_to(end)
            if n.key not in visited:
                queue.append(n)
    return current

MANIK = Node('MANIK', 40.69185, -8.61617)
ODEMI = Node('ODEMI', 37.49751, -8.38401)
TROIA = Node('TROIA', 38.07325, -8.87915)
UNOKO = Node('UNOKO', 50.45472, 7.22722)
INBOM = Node('INBOM', 40.00192, -8.30201)
UREDI = Node('UREDI', 39.85981, -6.39331)
CASPE = Node('CASPE', 41.26845, 0.19939)
TOSDI = Node('TOSDI', 40.99078, -6.28861)
DEPUL = Node('DEPUL', 45.92500, 5.49444)
NOSLI = Node('NOSLI', 59.07278, 17.25811)
ROUTE = route(TOSDI, UNOKO)
print(ROUTE.long_route())
print()
print(ROUTE.short_route())
