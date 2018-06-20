import random

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

class SnapNGo:
    def readFile(filename):
        Matrix = [[0 for x in range(19)] for y in range(19)]
        names = {}

        # for row in graph:
        #     for val in row:
        #         print '{:4}'.format(val),
        #     print

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
                names[v] = name
            else:
                edge = []
                for word in line.split(' '):
                    word = word.strip('\n')
                    edge.append(int(word))
                print edge[0]
                graph[edge[0]][edge[1]] = edge[2]

        # for row in graph:
        #     for val in row:
        #         print '{:4}'.format(val),
        #     print

    def randomDist():
        frm_num = random.randint(1,19)
        frm = g.get_vertex_id(frm_num)
        to_num = random.randint(1,19)
        to = g.get_vertex_id(to_num)

        task = Task(1, frm, to, '2018', 10, 5)
        print str(task)

def main():
    readFile("Wellesley_Outdoor_Map.txt")
    # randomDist()

if __name__ == '__main__':
    #when a follow request is received, follow them back and send a message.
    main()
