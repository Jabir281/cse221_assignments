def merge_sort(li):
    if len(li)<=1:
        return li
    mid=len(li)//2
    left=merge_sort(li[:mid])
    right=merge_sort(li[mid:])
    return merge(left,right)
def merge(left, right):
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged+=left[i:]
    merged+=right[j:]

    return merged



n=int(input())
li1=list(map(int,input().split()))
m=int(input())
li2=list(map(int,input().split()))
li3=li1+li2
sorted_li=merge_sort(li3)
for i in sorted_li:
    print(i,end=" ")

