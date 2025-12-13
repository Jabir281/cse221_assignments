def merge_sort(arr):
    if len(arr) <= 1:
        return arr, 0
    mid = len(arr) // 2
    left, left_inv = merge_sort(arr[:mid])
    right, right_inv = merge_sort(arr[mid:])

    merged = []
    i = j = 0
    inversions = left_inv + right_inv

    while i < len(left) and j < len(right):
        if left[i] > right[j] ** 2:
            inversions += len(left) - i
            j += 1
        else:
            i += 1
    merged = sorted(left + right)
    return merged, inversions



n = int(input())
arr = list(map(int, input().split()))
_, result = merge_sort(arr)
print(result)




