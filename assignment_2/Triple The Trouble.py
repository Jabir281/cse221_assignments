def make_list(n):
    li=[]
    for i,num in enumerate(n):
        li.append((num,i))
    return li


n, s = map(int, input().split())
li = list(map(int, input().split()))

li_sorted = sorted(make_list(li))


found = False
li2 = []

for i in range(n - 2):
    if found:
        break
    j, k = i + 1, n - 1
    while j < k:
        current_sum = li_sorted[i][0] + li_sorted[j][0] + li_sorted[k][0]
        if current_sum == s:
            li2 = sorted([li_sorted[i][1] , li_sorted[j][1] , li_sorted[k][1] ])
            found = True
            break
        elif current_sum < s:
            j += 1
        else:
            k -= 1

if found:
    print(f'{li2[0]+1} {li2[1]+1} {li2[2]+1}')
else:
    print(-1)