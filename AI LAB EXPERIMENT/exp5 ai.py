from collections import deque

def is_valid(m, c):
    return (m == 0 or m >= c) and (3-m == 0 or 3-m >= 3-c)

def solve():
    queue = deque([((3,3,1), [])])
    visited = set()

    while queue:
        state, path = queue.popleft()

        if state in visited:
            continue

        visited.add(state)
        path = path + [state]

        if state == (0,0,0):
            print("Solution:")
            for s in path:
                print(s)
            return

        m,c,b = state

        moves = [(1,0),(2,0),(0,1),(0,2),(1,1)]

        for dm,dc in moves:
            if b==1:
                nm,nc,nb = m-dm,c-dc,0
            else:
                nm,nc,nb = m+dm,c+dc,1

            if 0<=nm<=3 and 0<=nc<=3 and is_valid(nm,nc):
                queue.append(((nm,nc,nb),path))

solve()