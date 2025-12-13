from collections import deque


n, r = map(int, input().split())


adj = []
for _ in range(n + 1):
    adj.append([])
for _ in range(n - 1):
    u, v = map(int, input().split())
    adj[u].append(v)
    adj[v].append(u)


parent = [-1] * (n + 1)
li = []
q = deque([r])
parent[r] = 0

while q:
    u = q.popleft()
    li.append(u)
    for v in adj[u]:
        if parent[v] == -1:
            parent[v] = u
            q.append(v)


size = [1] * (n + 1)
for u in reversed(li):
    if u != r:
        size[parent[u]] += size[u]
num = int(input())
for _ in range(num):
    x = int(input())
    print(size[x])
