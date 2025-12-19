import heapq

n, m, s, d = map(int, input().split())
u_list = list(map(int, input().split()))
v_list = list(map(int, input().split()))
w_list = list(map(int, input().split()))

adj = []
for _ in range(n + 1):
    adj.append([])

for i in range(m):
    u, v, w = u_list[i], v_list[i], w_list[i]
    adj[u].append((v, w))

dist = [float('inf')] * (n + 1)
parent = [-1] * (n + 1)
dist[s] = 0

pq = []
heapq.heappush(pq, (0, s))

while pq:
    d_u, u = heapq.heappop(pq)
    
    if d_u > dist[u]:
        continue
    
    if u == d:
        break
        
    for v, w in adj[u]:
        if dist[u] + w < dist[v]:
            dist[v] = dist[u] + w
            parent[v] = u
            heapq.heappush(pq, (dist[v], v))

if dist[d] == float('inf'):
    print(-1)
else:
    print(dist[d])
    path = []
    curr = d
    while curr != -1:
        path.append(curr)
        curr = parent[curr]
    print(' '.join(map(str, path[::-1])))
