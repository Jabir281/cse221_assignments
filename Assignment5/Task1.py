from collections import deque

n, m = map(int, input().split())
li1=[]
for _ in range(n+1):
    li1.append([])
for _ in range(m):
    u, v = map(int, input().split())
    li1[u].append(v)
    li1[v].append(u)
for i in range(1, n + 1):
    li1[i].sort()
queue = deque()
li2 = [False] * (n + 1)
li3 = []
queue.append(1)
li2[1] = True
while queue:
    u = queue.popleft()
    li3.append(u)
    
    for v in li1[u]:
        if not li2[v]:
            li2[v] = True
            queue.append(v)

for i in li3:
    print(i, end=' ')