from collections import deque

n, m, s, q = map(int, input().split())

adj = []
for _ in range(n + 1):
    adj.append([])

for _ in range(m):
    u, v = map(int, input().split())
    adj[u].append(v)
    adj[v].append(u)

sources = list(map(int, input().split()))
dests = list(map(int, input().split()))

dist = [-1] * (n + 1)
q1 = deque()

for i in sources:
    dist[i] = 0
    q1.append(i)

while q1:
    u = q1.popleft()
    for v in adj[u]:
        if dist[v] == -1:
            dist[v] = dist[u] + 1
            q1.append(v)

res = []
for d in dests:
    res.append(str(dist[d]))
print(' '.join(res))