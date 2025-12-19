import heapq

n, m = map(int, input().split())

adj = []
for _ in range(n + 1):
    adj.append([])

for _ in range(m):
    u, v, w = map(int, input().split())
    adj[u].append((v, w))
    adj[v].append((u, w))

dist = [float('inf')] * (n + 1)
dist[1] = 0

pq = []
heapq.heappush(pq, (0, 1))

while pq:
    d_u, u = heapq.heappop(pq)
    
    if d_u > dist[u]:
        continue
    
    for v, w in adj[u]:
        new_danger = max(dist[u], w)
        
        if new_danger < dist[v]:
            dist[v] = new_danger
            heapq.heappush(pq, (dist[v], v))

res = []
for i in range(1, n + 1):
    if dist[i] == float('inf'):
        res.append(-1)
    else:
        res.append(dist[i])

print(' '.join(map(str, res)))
