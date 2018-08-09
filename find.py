#!/bin/bash/python3

import geopy.distance

with open('ats.txt') as f:
    ATS = f.readlines()

NEIGHBOURS = {}

class Node(object):
    def __init__(self, name, lat, lon, parent=None, g_cost=0.0):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.parent = parent
        self.g_cost = g_cost # distance from starting node
        self.h_cost = 0.0 # distance to goal

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

    def to_str(self):
        if not self.parent:
            return self.name
        return ' '.join([self.parent.to_str(), self.name])

    def distance_to(self, node):
        return geopy.distance.vincenty(
                (self.lat, self.lon),
                (node.lat, node.lon)
            ).nm

    @property
    def neighbours(self):
        if self.key in NEIGHBOURS:
            return NEIGHBOURS[self.key]

        result = set()
        for neighbour in ATS:
            if self.key not in neighbour:
                continue
            _, _, _, _, name, lat, lon, _, _, cost = neighbour.split(',')
            result.add(Node(
                    name, 
                    float(lat), 
                    float(lon), 
                    parent=self, 
                    g_cost=float(cost) + self.g_cost))
        
        NEIGHBOURS[self.key] = result    
        return result

def route(start, end):
    print('finding route from %s to %s' % (start.name, end.name))
    visited = set()
    queue = [(start),]
    current = None

    while not current or current.key != end.key:
        queue = sorted(queue, key=lambda x: x.f_cost)
        current = queue.pop(0)
        if current.key in visited:
            continue
        visited.add(current.key)
        for n in current.neighbours:
            n.h_cost = n.distance_to(end)
            if n.key not in visited:
                queue.append(n)
        print(current.to_str())
    return current

MANIK = Node('MANIK', 40.69185, -8.61617)
ODEMI = Node('ODEMI', 37.49751, -8.38401)
TROIA = Node('TROIA', 38.07325, -8.87915)
UNOKO = Node('UNOKO', 50.45472, 7.22722)
INBOM = Node('INBOM', 40.00192, -8.30201)
UREDI = Node('UREDI', 39.85981, -6.39331)
CASPE = Node('CASPE', 41.26845, 0.19939)
TOSDI = Node('TOSDI', 40.99078, -6.28861)
ROUTE = route(UREDI, CASPE)
print(ROUTE.to_str())
