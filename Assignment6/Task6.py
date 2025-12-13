from collections import deque

max_num = 5000
li = [0] * (max_num + 1)

for i in range(2, max_num + 1):
    if li[i] == 0:
        li[i] = i
        j = i * i
        while j <= max_num:
            if li[j] == 0:
                li[j] = i
            j += i

li1 =[]
for _ in range(max_num + 1):
    li1.append([])

for n in range(2, max_num + 1):
    x = n
    while x > 1:
        p = li[x]
        if p != n:
            li1[n].append(p)
        while x % p == 0:
            x //= p


t = int(input())
for _ in range(t):
    s_val, t_val = map(int, input().split())

    if s_val == t_val:
        print(0)
        continue

    if s_val > t_val:
        print(-1)
        continue

    dist = [-1] * (t_val + 1)
    q = deque()
    dist[s_val] = 0
    q.append(s_val)
    found = False

    while q:
        u = q.popleft()
        for p in li1[u]:
            v = u + p
            if v <= t_val and dist[v] == -1:
                dist[v] = dist[u] + 1
                if v == t_val:
                    found = True
                    break
                q.append(v)
        if found:
            break
    if found:
        print(dist[t_val])
    else:
        print(-1)
