n, k = map(int, input().split())
li = list(map(int, input().split()))

i = 0
freq = {}
max_len = 0

for j in range(n):
    freq[li[j]] = freq.get(li[j], 0) + 1
    
    while len(freq) > k and i <= j:
        freq[li[i]] -= 1
        if freq[li[i]] == 0:
            del freq[li[i]]
        i += 1
    
    max_len = max(max_len, j - i + 1)

print(max_len)