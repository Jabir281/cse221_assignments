def merge_sort_count(arr):
    if len(arr) <= 1:
        return 0, arr
    mid = len(arr) // 2
    l_count, l_sorted = merge_sort_count(arr[:mid])
    r_count, r_sorted = merge_sort_count(arr[mid:])
    merge_count, merged = merge(l_sorted, r_sorted)
    total_count = l_count + r_count + merge_count
    return total_count, merged

def merge(left, right):
    merged = []
    i = j = 0
    count = 0
    while i < len(left) and j < len(right):
        if left[i] <= (right[j])**2:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
            count += len(left) - i
    merged.extend(left[i:])
    merged.extend(right[j:])
    return count, merged


n = int(input())
li = list(map(int, input().split()))
inversions, li1 = merge_sort_count(li)
print(inversions)
print(' '.join(map(str,li1)))


