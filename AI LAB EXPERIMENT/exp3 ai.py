from collections import deque
def water_jug():
    visited = set()
    queue = deque([((0, 0), [])])
    while queue:
        (x, y), path = queue.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        path = path + [(x, y)]
        if x == 2:
            print("Solution:")
            for state in path:
                print(state)
            return
        next_states = [
            (4, y),                     
            (x, 3),                     
            (0, y),                     
            (x, 0),                      
            (x - min(x, 3-y), y + min(x, 3-y)),  
            (x + min(y, 4-x), y - min(y, 4-x))   
        ]

        for state in next_states:
            if state not in visited:
                queue.append((state, path))

water_jug()