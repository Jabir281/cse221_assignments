n, m = map(int, input().split())
li1 = list(map(int, input().split()))
li2 = list(map(int, input().split()))
li3 = [0] * (n + 1)
for i in range(m):
    u = li1[i]
    v = li2[i]
    if u == v:
        li3[u] += 2
    else:
        li3[u] += 1
        li3[v] += 1
odd_count = 0
for i in range(1, n + 1):
    if li3[i] % 2 == 1:
        odd_count += 1
if odd_count == 0 or odd_count == 2:
    print("YES")
else:
    print("NO")