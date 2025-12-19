import heapq

def dijkstra(n, start, adj):
    dist = [float('inf')] * (n + 1)
    dist[start] = 0
    pq = []
    heapq.heappush(pq, (0, start))
    
    while pq:
        d_u, u = heapq.heappop(pq)
        
        if d_u > dist[u]:
            continue
            
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
    return dist

n, m, s, t = map(int, input().split())

adj = []
for _ in range(n + 1):
    adj.append([])

for _ in range(m):
    u, v, w = map(int, input().split())
    adj[u].append((v, w))

dist_alice = dijkstra(n, s, adj)
dist_bob = dijkstra(n, t, adj)

min_time = float('inf')
meet_node = -1

for i in range(1, n + 1):
    if dist_alice[i] != float('inf') and dist_bob[i] != float('inf'):
        time_taken = max(dist_alice[i], dist_bob[i])
        if time_taken < min_time:
            min_time = time_taken
            meet_node = i
        elif time_taken == min_time:
            if meet_node == -1 or i < meet_node:
                meet_node = i

if meet_node != -1:
    print(f"{min_time} {meet_node}")
else:
    print(-1)
