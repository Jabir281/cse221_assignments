import heapq

n, m = map(int, input().split())

u_list = list(map(int, input().split()))
v_list = list(map(int, input().split()))
w_list = list(map(int, input().split()))

adj = []
for _ in range(n + 1):
    adj.append([])

for i in range(m):
    u, v, w = u_list[i], v_list[i], w_list[i]
    adj[u].append((v, w))

dist = []
for _ in range(n + 1):
    dist.append([float('inf')] * 3)

dist[1][2] = 0
pq = []
heapq.heappush(pq, (0, 1, 2))

while pq:
    d_u, u, last_p = heapq.heappop(pq)
    
    if d_u > dist[u][last_p]:
        continue
    
    for v, w in adj[u]:
        current_p = w % 2
        
        if last_p == 2 or last_p != current_p:
            if dist[u][last_p] + w < dist[v][current_p]:
                dist[v][current_p] = dist[u][last_p] + w
                heapq.heappush(pq, (dist[v][current_p], v, current_p))

ans = min(dist[n][0], dist[n][1])

if ans == float('inf'):
    print(-1)
else:
    print(ans)
