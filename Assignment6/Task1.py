from collections import deque

n, m = map(int, input().split())

adj = []
for _ in range(n + 1):
    adj.append([])

li1 = [0] * (n + 1)

for _ in range(m):
    a, b = map(int, input().split())
    adj[a].append(b)
    li1[b] += 1

for i in range(1, n + 1):
    adj[i].sort()

q = deque()
for i in range(1, n + 1):
    if li1[i] == 0:
        q.append(i)

res = []
while q:
    u = q.popleft()
    res.append(u)
    
    for v in adj[u]:
        li1[v] -= 1
        if li1[v] == 0:
            q.append(v)

if len(res) != n:
    print(-1)
else:
    print(' '.join(map(str, res)))