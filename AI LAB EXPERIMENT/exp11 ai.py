states = ['A', 'B', 'C', 'D']
graph = {'A':['B','C'], 'B':['A','C','D'], 'C':['A','B','D'], 'D':['B','C']}
colors = ['green','red','Blue']
ans = {}

def solve(i):
    if i == len(states):
        return True
    s = states[i]
    for c in colors:
        if all(ans.get(n) != c for n in graph[s]):
            ans[s] = c
            if solve(i + 1):
                return True
            del ans[s]

solve(0)
print(ans)