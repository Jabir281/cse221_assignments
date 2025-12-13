from collections import deque

n = int(input())
x1, y1, x2, y2 = map(int, input().split())

if x1 == x2 and y1 == y2:
    print(0)
else:
    dir_x = [2, 2, -2, -2, 1, 1, -1, -1]
    dir_y = [1, -1, 1, -1, 2, -2, 2, -2]
    
    dist = []
    for i in range(n + 1):
        dist.append([-1] * (n + 1))
    
    q = deque()
    dist[x1][y1] = 0
    q.append((x1, y1))
    
    found = False
    while q:
        x, y = q.popleft()
        for i in range(8):
            next_x = x + dir_x[i]
            next_y = y + dir_y[i]
            if 1 <= next_x <= n and 1 <= next_y <= n and dist[next_x][next_y] == -1:
                dist[next_x][next_y] = dist[x][y] + 1
                if next_x == x2 and next_y == y2:
                    found = True
                    break
                q.append((next_x, next_y))
        if found:
            break
    
    if found:
        print(dist[x2][y2])
    else:
        print(-1)