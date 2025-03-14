# -*- coding: utf-8 -*-

class Node(object):
    def __init__(self, k, v):
        self.key = k
        self.val = v
        self.prev = Node
        self.next = Node


class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.hkeys = {}

        self.top = Node(Node, -1)
        self.tail = Node(Node, -1)
        self.top.next = self.tail
        self.tail.prev = self.top

    def put(self, k, v):
        if k in self.hkeys:
            cur = self.hkeys[k]
            cur.val = v

            cur.prev.next = cur.next
            cur.next.prev = cur.prev

            top_node = self.top.next
            self.top.next = cur
            cur.prev = self.top
            cur.next = top_node
            top_node.prev = cur
        else:
            cur = Node(k, v)
            self.hkeys[k] = cur

            top_node = self.top.next
            self.top.next = cur
            cur.prev = self.top
            cur.next = top_node
            top_node.prev = cur

            if len(self.hkeys.keys()) > self.cap:
                self.hkeys.pop(self.tail.prev.key)
                self.tail.prev.prev.next = self.tail
                self.tail.prev = self.tail.prev.prev

    def get(self, k):
        if k in self.hkeys:
            cur = self.hkeys[k]

            cur.prev.next = cur.next
            cur.next.prev = cur.prev

            top_node = self.top.next
            self.top.next = cur
            cur.prev = self.top
            cur.next = top_node
            top_node.prev = cur

            return self.hkeys[k].val
        return -1

    def _del(self):
        pass

    def __repr__(self):
        vals = []
        p = self.top.next
        while p.next:
            vals.append(str(p.val))
            p = p.next
        return '->'.join(vals)


cache = LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
print(cache)
