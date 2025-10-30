def make_list(n):
    li=[]
    for i,num in enumerate(n):
        li.append((num,i))
    return li


n, m, k = map(int, input().split())
li1 = list(map(int, input().split()))
li2 = list(map(int, input().split()))


li1_sorted = sorted(make_list(li1))
li2_sorted = sorted(make_list(li2))

i, j = 0, m - 1
min_diff = float('inf')
sum = (0, 0)


while i < n and j >= 0:
    current_sum = li1_sorted[i][0] + li2_sorted[j][0]
    current_diff = abs(current_sum - k)
    
 
    if current_diff < min_diff:
        min_diff = current_diff
        sum = (li1_sorted[i][1], li2_sorted[j][1])
    

    if current_sum < k:
        i+= 1
    else:
        j-= 1

print(f'{sum[0] + 1} {sum[1] + 1}')
