from collections import deque
goal = ((1, 2, 3),
        (4, 5, 6),
        (7, 8, 0))

start = ((1, 2, 3),
         (4, 6, 0),
         (7, 5, 8))

queue = deque([(start, [])])
visited = {start}

while queue:
    state, path = queue.popleft()

    if state == goal:
        print("Solution Found!\n")
        for step in path + [state]:
            for row in step:
                print(row)
            print()
        break

    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                x, y = i, j

    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
        nx, ny = x + dx, y + dy

        if 0 <= nx < 3 and 0 <= ny < 3:
            temp = [list(r) for r in state]
            temp[x][y], temp[nx][ny] = temp[nx][ny], temp[x][y]
            new_state = tuple(tuple(r) for r in temp)

            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, path + [state]))