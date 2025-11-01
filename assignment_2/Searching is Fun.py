t = int(input())
for _ in range(t):
    k, x = map(int, input().split())
    result = k + (k - 1) // (x - 1)
    print(result)
        


