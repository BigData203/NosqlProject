




# 构建小顶堆跳转
def sift(li, low, higt):
    tmp = li[low]
    i = low
    j = 2 * i + 1
    while j <= higt:  # 情况2：i已经是最后一层
        if j + 1 <= higt and li[j + 1][1] < li[j][1]:  # 右孩子存在并且小于左孩子
            j += 1
        if tmp[1] > li[j][1]:
            li[i] = li[j]
            i = j
            j = 2 * i + 1
        else:
            break  # 情况1：j位置比tmp小
    li[i] = tmp


def top_k(li, k):
    heap = li[0:k]
    # 建堆
    for i in range(k // 2 - 1, -1, -1):
        sift(heap, i, k - 1)
    for i in range(k, len(li)):
        if li[i][1] > heap[0][1]:
            heap[0] = li[i]
            sift(heap, 0, k - 1)
    # 挨个输出
    for i in range(k - 1, -1, -1):
        heap[0], heap[i] = heap[i], heap[0]
        sift(heap, 0, i - 1)
    return heap

#top_k(li,10)
#li=[list(i)  for i in tf_idf.items()]#元组转列表
#li[:10]

#li = [[0, 8], [6, 2], [4, 9], [1, 4], [6,11]]
#print(top_k(li, 3))