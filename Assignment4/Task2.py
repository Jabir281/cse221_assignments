n, m = map(int, input().split())

u_li = list(map(int, input().split()))
v_li = list(map(int, input().split()))
w_li = list(map(int, input().split()))

adj_li = []
for i in range(n+1):
    adj_li.append([])

for i in range(m):
    u = u_li[i]
    v = v_li[i]
    w = w_li[i]
    adj_li[u].append((v, w))

for i in range(1, n+1):
    print(f"{i}:", end="")
    for j in range(len(adj_li[i])):
        print(f" ({adj_li[i][j][0]},{adj_li[i][j][1]})", end="")
    print()