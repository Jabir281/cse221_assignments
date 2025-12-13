n = int(input())

matrix = []
for i in range(n):
    row = []
    for j in range(n):
        row.append(0)
    matrix.append(row)

for i in range(n):
    line = list(map(int, input().split()))
    k = line[0]
    for j in range(1, k + 1):
        l = line[j]
        matrix[i][l] = 1

for i in range(n):
    for j in range(n):
        print(matrix[i][j], end=" ")
    print()