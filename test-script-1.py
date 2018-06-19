import random

# class Vertex:
#     def __init__(self, node, name):
#         self.id = node
#         self.name = name
#         self.adjacent = {}
#
#     def __str__(self):
#         return str(self.id) + ' adjacent: ' + str([x.id for x in self.adjacent])
#
#     def add_neighbor(self, neighbor, weight=0):
#         self.adjacent[neighbor] = weight
#
#     def get_connections(self):
#         return self.adjacent.keys()
#
#     def get_id(self):
#         return self.id
#
#     def get_name(self):
#         return self.name
#
#     def get_weight(self, neighbor):
#         return self.adjacent[neighbor]
#
# class Graph:
#     def __init__(self):
#         self.vert_dict = {}
#         self.num_vertices = 0
#
#     def __iter__(self):
#         return iter(self.vert_dict.values())
#
#     def add_vertex(self, id, name):
#         v = Vertex(id, name)
#         self.vert_dict[id] = v
#         return v
#
#     def get_vertex_id(self, id):
#         return self.vert_dict[id]
#
#     def add_edge(self, frm, to, cost):
#         if frm not in self.vert_dict or to not in self.vert_dict:
#             print "Node(s) not in graph"
#
#         self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)
#         self.vert_dict[to].add_neighbor(self.vert_dict[frm], cost)
#
#     def get_vertices(self):
#         return self.vert_dict.keys()

class Task:
    def __init__(self, id, start, end, datetime, duration, compensation):
        self.id = id
        self.startLocation = start
        self.endLocation = end
        self.datetime = datetime
        self.compensation = compensation
        self.duration = duration

    def __str__(self):
        return 'Task ID: ' + str(self.id) + '\t Location: ' + str(self.startLocation) + '\t Date: ' + str(self.datetime) + '\t Compensation:' + str(self.compensation) + '\n'


def readFile(filename):
    with open(filename, "r") as f:
        content = f.readlines()

    edges = False
    for line in content:
        v = line.split(' ', 1)[0]
        if v == "#\n":
            edges = True
            continue
        if edges is False:
            name = line.split(' ', 1)[1]
            g[][]
        else:
            edge = []
            for word in line.split(' '):
                word = word.strip('\n')
                edge.append(int(word))
            g.add_edge(edge[0], edge[1], edge[2])

    # for v in g:
    #     for w in v.get_connections():
    #         vid = v.get_id()
    #         wid = w.get_id()
    #         print '( %s , %s, %3d)'  % ( vid, wid, v.get_weight(w))
    #
    # for v in g:
    #     print 'g.vert_dict[%s]=%s' %(v.get_id(), g.vert_dict[v.get_id()])

def randomDist():
    frm_num = random.randint(1,19)
    frm = g.get_vertex_id(frm_num)
    to_num = random.randint(1,19)
    to = g.get_vertex_id(to_num)

    task = Task(1, frm, to, '2018', 10, 5)
    print str(task)

def main():
    readFile("Wellesley_Outdoor.txt")
    randomDist()

if __name__ == '__main__':
    #when a follow request is received, follow them back and send a message.
    main()
