n, k = map(int, input().split())
arr = list(map(int, input().split()))

left = 0
current_sum = 0
max_length = 0

for right in range(n):
    current_sum += arr[right]
    while current_sum > k and left <= right:
        current_sum -= arr[left]
        left += 1
    max_length = max(max_length, right - left + 1)

print(max_length)