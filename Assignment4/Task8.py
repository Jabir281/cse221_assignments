def co_prime(a, b):
    while b:
        a, b = b, a % b
    return a 
n, q = map(int, input().split())
li1 = []
for i in range(1, n + 1):
    li2 = []
    for j in range(1, n + 1):
        if i != j and co_prime(i, j) == 1:
            li2.append(j)
    li1.append(li2)
li3 = []
for _ in range(q):
    x, k = map(int, input().split())
    if k <= len(li1[x - 1]):
        li3.append(str(li1[x - 1][k - 1]))
    else:
        li3.append("-1")
for i in range(len(li3)):
    print(li3[i])