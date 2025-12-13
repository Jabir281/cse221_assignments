from collections import deque

r,h = map(int, input().split())
grid = []
for _ in range(r):
    row = list(input().strip())
    grid.append(row)

vis = []
for i in range(r):
    n = [False] * h
    vis.append(n)      
dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
max_diamonds = 0

for i in range(r):
    for j in range(h):
        if grid[i][j] != '#' and not vis[i][j]:
            q = deque()
            q.append((i, j))
            vis[i][j] = True
            cnt = 0
            while q:
                x, y = q.popleft()
                if grid[x][y] == 'D':
                    cnt += 1
                for x1, y1 in dirs:
                    x2, y2 = x + x1, y + y1
                    if 0 <= x2 < r and 0 <= y2 < h and grid[x2][y2] != '#' and not vis[x2][y2]:
                        vis[x2][y2] = True
                        q.append((x2, y2))
            max_diamonds = max(max_diamonds, cnt)

print(max_diamonds)