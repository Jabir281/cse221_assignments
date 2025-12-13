def sort(arr):
    even = arr[0::2][::-1]   
    odd  = arr[1::2]        
    i = j = 0
    merged = []
    while i < len(even) and j < len(odd):
        if even[i] < odd[j]:
            merged.append(even[i])
            i += 1
        else:
            merged.append(odd[j])
            j += 1


    merged.extend(even[i:])
    merged.extend(odd[j:])
    return merged
