n, m, k = map(int, input().split())
found= False
li = []
dict1 = {}
for _ in range(k):
    x, y = map(int, input().split())
    dict1[(x, y)] = True
    li.append((x, y))
dir_x = [-2, -2, -1, -1, 1, 1, 2, 2]
dir_y = [-1, 1, -2, 2, -2, 2, -1, 1]
for x, y in li:
    for i in range(len(dir_x)):
        x1 = dir_x[i]
        y1 = dir_y[i]
        x2 = x + x1
        y2 = y + y1
        if 1 <= x2 <= n and 1 <= y2 <= m:
            if (x2, y2) in dict1:
                found = True
                break
    if found:
        break
if found:
    print("YES")
else:
    print("NO")

                
                

