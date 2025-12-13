import heapq

n = int(input())
words = []
for _ in range(n):
    words.append(input().strip())


all = set()
for w in words:
    for ch in w:
        all.add(ch)

letter_l = sorted(all)

idx = {}
for i in range(26):
    idx[chr(ord('a') + i)] = i

letter = {}
for i in range(26):
    letter[i] = chr(ord('a') + i)


adj = []
for _ in range(26):
    adj.append([])
li = [0] * 26

valid = True
for i in range(n - 1):
    w1 = words[i]
    w2 = words[i + 1]
    min_len = min(len(w1), len(w2))
    found_diff = False

    for j in range(min_len):
        if w1[j] != w2[j]:
            u = idx[w1[j]]
            v = idx[w2[j]]
            adj[u].append(v)
            li[v] += 1
            found_diff = True
            break

    if not found_diff and len(w1) > len(w2):
        valid = False
        break

if not valid:
    print(-1)
else:
    heap = []
    for ch in all:
        l_idx = idx[ch]
        if li[l_idx] == 0:
            heapq.heappush(heap, ch)

    res = []
    while heap:
        ch = heapq.heappop(heap)
        res.append(ch)
        u = idx[ch]

        for v in adj[u]:
            li[v] -= 1
            if li[v] == 0:
                heapq.heappush(heap, letter[v])

    if len(res) != len(all):
        print(-1)
    else:
        print("".join(res))
