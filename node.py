#!/usr/bin/bash/python3

from collections import defaultdict
from geopy import distance
from csv import reader as csvreader

NODES = defaultdict(list)

class Node(object):
    def __init__(self, name, lat, lon, region):
        self.name = name
        self.location = (float(lat), float(lon))
        self.region = region

        self.g_cost = 0.0
        self.h_cost = 0.0
        self.via = 'DCT'
        self.neighbours = list()

        NODES[name].append(self)

    def load(name, *args, **kwargs):
        if name not in NODES:
            raise LookupError('%s did not match any node' % name)
        
        candidates = NODES[name]

        if len(candidates) == 1:
            return candidates[0]

        location = None
        if 'lat' in kwargs and 'lon' in kwargs:
            location = (float(kwargs['lat']), float(kwargs['lon']))
        if 'location' in kwargs:
            location = kwargs['location']

        if not location:
            raise LookupError('Multiple matches for %s' % name)

        candidates_by_distance = [
                (node, distance.vincenty(node.location, location))
                for node in candidates]

        return min(candidates_by_distance, key=lambda x: x[1])[0]

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
        return distance.vincenty(self.location, node.location).nm

with open('navdata/Waypoints.txt') as f:
    reader = csvreader(f, delimiter=',')
    for line in reader:
        if len(line) == 0:
            continue
        Node(*line)
with open('navdata/Navaids.txt') as f:
    reader = csvreader(f, delimiter=',')
    for line in reader:
        if len(line) == 0:
            continue
        name, _,_,_,_,_, lat, lon, _, region, *_ = line
        Node(name, lat, lon, region)
with open('navdata/ats.txt') as f:
    reader = csvreader(f, delimiter=',')
    for line in reader:
        if len(line) == 0:
            continue
        t, *_ = line
        if t == 'A':
            _, airway, _ = line
        elif t == 'S':
            _, name, lat, lon, nname, nlat, nlon, _, _, ncost = line
            parent = Node.load(name, lat=lat, lon=lon)
            node = Node.load(nname, lat=nlat, lon=nlon)
            parent.neighbours.append((airway, float(ncost), node))
