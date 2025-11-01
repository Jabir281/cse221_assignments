n, k = map(int, input().split())
li = list(map(int, input().split()))

i = 0
dict1 = {}
max_len = 0

for j in range(n):
    dict1[li[j]] = dict1.get(li[j], 0) + 1
    
    while len(dict1) > k and i <= j:
        dict1[li[i]] -= 1
        if dict1[li[i]] == 0:
            del dict1[li[i]]
        i += 1
    len1=j - i + 1
    max_len = max(max_len, len1)

print(max_len)