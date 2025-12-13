from collections import deque

n = int(input())

adj = []
for _ in range(n + 1):
    adj.append([])

for _ in range(n - 1):
    u, v = map(int, input().split())
    adj[u].append(v)
    adj[v].append(u)

def bfs(start):
    dist = [-1] * (n + 1)
    q = deque([start])
    dist[start] = 0
    while q:
        u = q.popleft()
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)
    max_dist = -1
    far = start
    for i in range(1, n + 1):
        if dist[i] > max_dist:
            max_dist = dist[i]
            far = i
    return far, max_dist

u, _ = bfs(1)
v, d = bfs(u)

print(d)
print(u, v)