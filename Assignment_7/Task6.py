import heapq

n, m, s, d = map(int, input().split())

adj = []
for _ in range(n + 1):
    adj.append([])

for _ in range(m):
    u, v, w = map(int, input().split())
    adj[u].append((v, w))
    adj[v].append((u, w))

dist1 = [float('inf')] * (n + 1)
dist2 = [float('inf')] * (n + 1)

dist1[s] = 0
pq = []
heapq.heappush(pq, (0, s))

while pq:
    d_u, u = heapq.heappop(pq)
    
    if d_u > dist2[u]:
        continue
        
    for v, w in adj[u]:
        new_dist = d_u + w
        
        if new_dist < dist1[v]:
            dist2[v] = dist1[v]
            dist1[v] = new_dist
            heapq.heappush(pq, (dist1[v], v))
            heapq.heappush(pq, (dist2[v], v))
            
        elif dist1[v] < new_dist < dist2[v]:
            dist2[v] = new_dist
            heapq.heappush(pq, (dist2[v], v))

if dist2[d] == float('inf'):
    print(-1)
else:
    print(dist2[d])
