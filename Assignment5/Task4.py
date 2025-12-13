from collections import deque

def bfs(s, adj, n):
    dis = [-1] * (n + 1)
    p = [-1] * (n + 1)
    q = deque()
    dis[s] = 0
    q.append(s)

    while q:
        u = q.popleft()
        for v in adj[u]:
            if dis[v] == -1:
                dis[v] = dis[u] + 1
                p[v] = u
                q.append(v)

    return dis, p


def get_path(s, end, li):
    p = []
    current = end
    while current != -1:
        p.append(current)
        current = li[current]
    p.reverse()

    if p[0] != s:
        return None
    return p



n, m, s, d, k = map(int, input().split())

adj = []
for _ in range(n + 1):
    adj.append([])
u_li = []
v_li = []

for _ in range(m):
    u, v = map(int, input().split())
    u_li.append(u)
    v_li.append(v)
    adj[u].append(v)



if s == d and s == k:
    print(0)
    print(s)
else:
    li3, li4 = bfs(s, adj, n)
    li5, li6 = bfs(k, adj, n)

    if li3[k] == -1 or li5[d] == -1:
        print(-1)
    else:
        path1 = get_path(s, k, li4)
        path2 = get_path(k, d, li6)

        if not path1 or not path2:
            print(-1)
        else:
            li_f = path1 + path2[1:]
            print(len(li_f) - 1)
            print(" ".join(map(str, li_f)))
