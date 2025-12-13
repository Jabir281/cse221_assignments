n, m = map(int, input().split())
adj = []
for _ in range(n + 1):
    adj.append([])  
for _ in range(m):
    u, v = map(int, input().split())
    adj[u].append(v)

vis = [0] * (n + 1)  
found = False

for i in range(1, n + 1):
    if vis[i] != 0:
        continue
    stack = [i]
    while stack:
        u = stack[-1]
        if vis[u] == 0:
            vis[u] = 1
            for v in adj[u]:
                if vis[v] == 0:
                    stack.append(v)
                elif vis[v] == 1:
                    found = True
                    break
            if found:
                break
        else:
            vis[u] = 2
            stack.pop()
    if found:
        break

if found:
    print("YES")
else:
    print("NO") 
