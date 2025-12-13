import sys
sys.setrecursionlimit(10**7)

data = sys.stdin.read().split()
n = int(data[0])
m = int(data[1])

adj = [[] for _ in range(n + 1)]

for i in range(m):
    u = int(data[2 + i])
    v = int(data[2 + m + i])
    adj[u].append(v)
    adj[v].append(u)

for i in range(1, n + 1):
    adj[i].sort()

visited = [False] * (n + 1)
order = []
stack = [1]

while stack:
    u = stack.pop()
    if not visited[u]:
        visited[u] = True
        order.append(u)
        for v in reversed(adj[u]):
            if not visited[v]:
                stack.append(v)

for node in order:
    print(node, end=' ')