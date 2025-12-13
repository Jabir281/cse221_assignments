n, m = map(int, input().split())
u = list(map(int, input().split()))
v = list(map(int, input().split()))

adj = []
for _ in range(n + 1):
    adj.append([])
for i in range(m):
    a, b = u[i], v[i]
    adj[a].append(b)
    adj[b].append(a)


for i in range(1, n + 1):
    adj[i].sort(reverse=True)  

vis = [False] * (n + 1)
res = []

stack = [1]  

while stack:
    node = stack.pop()
    if not vis[node]:
        vis[node] = True
        res.append(node)
        for nxt in adj[node]:
            if not vis[nxt]:
                stack.append(nxt)

print(' '.join(map(str, res)))
