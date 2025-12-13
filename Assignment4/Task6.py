n = int(input())
x1, y1 = map(int, input().split())
li = []
dir_x = [-1, -1, -1, 0, 0, 1, 1, 1]
dir_y = [-1, 0, 1, -1, 1, -1, 0, 1]
for i in range(8):
    x2 = x1 + dir_x[i]
    y2 = y1 + dir_y[i]
    if 1 <= x2 <= n and 1 <= y2 <= n:
        li.append((x2, y2))
li.sort()
print(len(li))
for i in range(len(li)):
    print(li[i][0], li[i][1])