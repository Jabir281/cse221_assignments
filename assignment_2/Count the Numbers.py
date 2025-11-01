def count(li, x, y):
    i, j = 0, len(li)
    while i < j:
        mid = (i + j) // 2
        if li[mid] < x:
            i = mid + 1
        else:
            j = mid
    start = i
    
    i, j = 0, len(li)
    while i < j:
        mid = (i + j) // 2
        if li[mid] <= y:
            i = mid + 1
        else:
            j = mid
    end = i
    
    return end - start
n, q = map(int, input().split())
li1 = list(map(int, input().split()))
for _ in range(q):
    x, y = map(int, input().split())
    print(count(li1, x, y))