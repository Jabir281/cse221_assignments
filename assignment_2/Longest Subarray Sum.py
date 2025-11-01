n, k = map(int, input().split())
li = list(map(int, input().split()))

i = 0
current_sum = 0
max_len = 0

for j in range(n):
    current_sum += li[j]
    while current_sum > k and i <= j:
        current_sum -= li[i]
        i += 1
        len1=j - i + 1
    max_len = max(max_len, len1)

print(max_len)