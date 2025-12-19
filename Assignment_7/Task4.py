import heapq

n, m, s, d = map(int, input().split())

node_weights = list(map(int, input().split()))
weights = [0] + node_weights

adj = []
for _ in range(n + 1):
    adj.append([])

for _ in range(m):
    u, v = map(int, input().split())
    adj[u].append(v)

dist = [float('inf')] * (n + 1)
dist[s] = weights[s]

pq = []
heapq.heappush(pq, (dist[s], s))

while pq:
    d_u, u = heapq.heappop(pq)
    
    if d_u > dist[u]:
        continue
    
    if u == d:
        break
        
    for v in adj[u]:
        if dist[u] + weights[v] < dist[v]:
            dist[v] = dist[u] + weights[v]
            heapq.heappush(pq, (dist[v], v))

if dist[d] == float('inf'):
    print(-1)
else:
    print(dist[d])
