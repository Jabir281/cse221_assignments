n, m = map(int, input().split())

matrix = []
for i in range(n):
    row = []
    for j in range(n):
        row.append(0)
    matrix.append(row)

for _ in range(m):
    u, v, w = map(int, input().split())
    matrix[u-1][v-1] = w

for i in range(n):
    for j in range(n):
        print(matrix[i][j], end=" ")
    print()