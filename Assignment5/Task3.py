from collections import deque

def bfs(start, adj, n):
    dist = [-1] * (n + 1)
    q = deque()
    dist[start] = 0
    q.append(start)

    while q:
        u = q.popleft()
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)

    return dist




n, m, s, d = map(int, input().split())
u_li=list(map(int, input().split()))
v_li=list(map(int, input().split()))


adj = []
for _ in range(n + 1):
    adj.append([])

for i in range(m):
    u = u_li[i]
    v = v_li[i]
    adj[u].append(v)
    adj[v].append(u)


if s == d:
    print(0)
    print(s)
else:
    dist1 = bfs(s, adj, n)

    if dist1[d] == -1:
        print(-1)
    else:
        dist2 = bfs(d, adj, n)

        path = [s]
        curr = s

        while curr != d:
            li = []

            for v in adj[curr]:
                if (dist1[v] == dist1[curr] + 1 and
                    dist1[v] + dist2[v] == dist1[d]):
                    li.append(v)

            next_node = min(li)
            path.append(next_node)
            curr = next_node

        print(len(path) - 1)
        print(' '.join(map(str, path)))
