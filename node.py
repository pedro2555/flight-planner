#!/usr/bin/bash/python3

from collections import defaultdict
from geopy import distance
from csv import reader as csvreader
from os import listdir

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
        location = None
        if 'lat' in kwargs and 'lon' in kwargs:
            location = (float(kwargs['lat']), float(kwargs['lon']))
        if 'location' in kwargs:
            location = kwargs['location']

        if name not in NODES:
            NODES[name].append(Node(name, lat, lon, ''))
        
        candidates = NODES[name]

        if len(candidates) == 1:
            return candidates[0]

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
                '{:.5f}'.format(self.location[0]),
                '{:.5f}'.format(self.location[0])])

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

            parent = Node.load(name, lat=lat, lon=lon)
            node = Node.load(nname, lat=nlat, lon=nlon)

            cost = node.distance_to(parent)
            parent.neighbours.append(('DCT', cost, node))
            node.neighbours.append(('DCT', cost, parent))
