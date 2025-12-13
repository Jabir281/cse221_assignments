n, m = map(int, input().split())
li1 = list(map(int, input().split()))
li2 = list(map(int, input().split()))
li3 = [0] * (n + 1)
for i in range(m):
    u = li1[i]
    v = li2[i]
    li3[u] -= 1
    li3[v] += 1
for i in range(1, n + 1):
    print(li3[i], end=" ")