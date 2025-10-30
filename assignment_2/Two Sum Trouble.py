n,s=map(int,input().split(" "))
li=list(map(int, input().split(" ")))
dict_1={}
flag= 0
for i,num in enumerate(li,start=1):
    sub=s-num
    if sub in dict_1:
        print(f'{dict_1[sub]} {i}')
        flag=1
        break
    dict_1[num]=i
if flag==0:
    print(-1)
    

