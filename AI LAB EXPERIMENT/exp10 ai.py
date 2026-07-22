from queue import PriorityQueue
graph = {'A':[('B',1),('C',3)], 'B':[('D',3),('E',1)],
         'C':[('F',5)], 'D':[('G',2)],
         'E':[('G',4)], 'F':[('G',2)], 'G':[]}
h = {'A':7,'B':6,'C':4,'D':2,'E':1,'F':1,'G':0}

pq = PriorityQueue()
pq.put((0,'A'))
cost = {'A':0}
parent = {'A':None}

while not pq.empty():
    x = pq.get()[1]
    if x == 'G':
        break
    for y,w in graph[x]:
        c = cost[x] + w
        if y not in cost or c < cost[y]:
            cost[y] = c
            pq.put((c+h[y], y))
            parent[y] = x

path = []
node = 'G'
while node:
    path.append(node)
    node = parent[node]

print("Path:", path[::-1])
print("Cost:", cost['G'])