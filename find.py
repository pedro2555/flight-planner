#!/bin/bash/python3

import csv
from collections import defaultdict
import geopy.distance
from os import listdir

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
        for neighbour in WPTS[self.key]:
            neighbour.g_cost = neighbour.cost + self.g_cost
            neighbour.parent = self
            result.add(neighbour)
        return result

WPTS = defaultdict(list)
for dct in listdir('navdata/DCTS'):
    with open('/'.join(['navdata/DCTS', dct])) as f:
        reader = f.readlines()
        for line in reader:
            if len(line) == 0:
                continue

            name = line[77:77 + 5].strip()
            if name == '' or name[0:1].isdigit():
                continue
            lat = float('.'.join([line[26:26+3], line[26+3:26+9]]))
            lon = float('.'.join([line[35:35+3], line[35+3:35+9]]))

            nname = line[87:87 + 5].strip()
            if nname == '' or nname[0:1].isdigit():
                continue
            nlat = float('.'.join([line[45:45+3], line[45+3:45+9]]))
            nlon = float('.'.join([line[54:54+3], line[54+3:54+9]]))

            parent = Node(name, float(lat), float(lon))
            node = Node(
                    nname,
                    float(nlat),
                    float(nlon),
                    via='DCT')
            node.cost = node.distance_to(parent)
            parent.cost = node.cost

            WPTS[parent.key].append(node)
            WPTS[node.key].append(parent)

with open('navdata/ats.txt') as f:
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
            node = Node(nname, float(nlat), float(nlon))

            node.cost = float(ncost)
            node.via = airway

            WPTS[parent.key].append(node)

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

IXIDA = Node('IXIDA', 39.654999, -0.80167)
INBOM = Node('INBOM', 40.001944, -8.301944)
UNOKO = Node('UNOKO', 50.454722, 7.227222)

ROUTE = route(IXIDA, UNOKO)
print(ROUTE.long_route())
print()
print(ROUTE.short_route())
