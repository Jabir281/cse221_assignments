from collections import deque

n, m = map(int, input().split())

adj = []
for _ in range(n + 1):
    adj.append([])

for _ in range(m):
    u, v = map(int, input().split())
    adj[u].append(v)
    adj[v].append(u)

li = [-1] * (n + 1)
ans = 0
poss = True

for i in range(1, n + 1):
    if li[i] == -1:
        q = deque()
        q.append(i)
        li[i] = 0
        x = 1
        y = 0
        while q:
            u = q.popleft()
            for v in adj[u]:
                if li[v] == -1:
                    li[v] = 1 - li[u]
                    if li[v] == 0:
                        x += 1
                    else:
                        y += 1
                    q.append(v)
                else:
                    if li[v] == li[u]:
                        poss = False
                        break
            if not poss:
                break
        if not poss:
            break
        ans += max(x, y)

if poss:
    print(ans)
else:
    print(-1)