#!/usr/bin/python3

from node import Node

class RouteNode(object):
    def __init__(self, node, via='DCT', cost=0.0, parent=None):
        self.node = node
        self.via = via
        self.cost = cost
        self.parent = parent

    def route(self, end):
        visited = set()
        # via, cost, node, parent
        queue = [(self),]
        current = None

        while not current or current.node.key != end.key:
            queue = sorted(queue, key=lambda x: x.cost)
            current = queue.pop(0)

            # pass only once per WPT
            if current.node.key in visited:
                continue
            visited.add(current.node.key)

            for neighbour in current.node.neighbours:
                via, cost, node = neighbour
                if node.key not in visited:
                    queue.append(RouteNode(
                            node,
                            via=via,
                            cost=cost + node.distance_to(end),
                            parent=current))
        return current

    def long_route(self):
        if not self.parent:
            return self.node.name
        return ' '.join([self.parent.long_route(), self.via, self.node.name])

    def short_route(self, via=None):
        if not self.parent:
            return self.node.name

        if not via or via != self.via:
            return ' '.join([self.parent.short_route(via=self.via),
                                                     self.via,
                                                     self.node.name])
        return self.parent.short_route(via=self.via)

start = Node.load('INBOM')
end = Node.load('UNOKO')
print('route %s - %s' % (start, end))

RouteNode(start).route(end).long_route()
