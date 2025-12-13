import sys
sys.setrecursionlimit(2*10**5)

def dfs(u):
    vis[u] = 1
    for v in adj[u]:
        if vis[v] == 0:
            if dfs(v):       
                return True
        elif vis[v] == 1:    
            return True
    vis[u] = 2
    return False  



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
    if vis[i] == 0:
        found = dfs(i)
        if found:
            break

if found:
    print("YES")
else:
    print("NO")
