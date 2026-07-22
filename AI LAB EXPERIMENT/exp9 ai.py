from itertools import permutations

graph = [
    [0,10,15,20],
    [10,0,35,25],
    [15,35,0,30],
    [20,25,30,0]
]

n = len(graph)
cities = list(range(1,n))

min_cost = float('inf')

for p in permutations(cities):
    cost = graph[0][p[0]]

    for i in range(len(p)-1):
        cost += graph[p[i]][p[i+1]]

    cost += graph[p[-1]][0]

    if cost < min_cost:
        min_cost = cost
        best_path = (0,) + p + (0,)

print("Minimum Cost =", min_cost)
print("Path =", best_path)