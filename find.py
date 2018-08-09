#!/bin/bash/python3

import geopy.distance

class Node(object):
    def __init__(self, name, lat, lon, parent=None, cost=0.0):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.parent = parent
        self.cost = cost

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
        result = set()
        with open('ats.txt') as f:
            lines = f.readlines()
            _neighbours = [l for l in lines
                      if self.key in l]

        for neighbour in _neighbours:
            _, _, _, _, name, lat, lon, _, _, cost = neighbour.split(',')
            result.add(Node(
                    name, 
                    float(lat), 
                    float(lon), 
                    parent=self, 
                    cost=float(cost)))
        return result

def route(start, end):
    print('finding route from %s to %s' % (start.name, end.name))
    visited = set()
    queue = [(start),]
    current = None

    while not current or current.key != end.key:
        queue = sorted(queue, key=lambda x: x.cost)
        current = queue.pop(0)
        if current.key in visited:
            continue
        visited.add(current.key)
        for n in current.neighbours:
            n.cost += current.cost + n.distance_to(end)
            if n.key not in visited:
                queue.append(n)
        print(current.name, current.cost)
    return current

MANIK = Node('MANIK', 40.69185, -8.61617)
ODEMI = Node('ODEMI', 37.49751, -8.38401)
TROIA = Node('TROIA', 38.07325, -8.87915)
UNOKO = Node('UNOKO', 50.45472, 7.22722)
INBOM = Node('INBOM', 40.00192, -8.30201)
ROUTE = route(MANIK, ODEMI)
print(ROUTE.to_str())
ROUTE = route(INBOM, UNOKO)
print(ROUTE.to_str())
