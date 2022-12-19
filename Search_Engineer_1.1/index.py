"""
建倒排索引
"""
import jieba
import math

class Doc:
    def __init__(self):
        self.field = {}

    def add(self, field, content):
        self.field[field] = content

    def get(self, field):
        return self.field[field]
    


#--------1.读取文件
import os
import re
texts=[]

fname=os.listdir('./static/doc')
fname.sort(key= lambda x:int(x[:-4]))
for file in fname:
    texts.append(open('./static/doc/'+file,encoding="utf-8").read())

do1=[]
index=0
doc_list = []
for i in texts:#获取文档对应部分的内容
    a=i.split('\n\n\n',1)
    summart_conent=a[1].split('\n\n\n',1)
    title_link=b=a[0].split()
    doc = Doc()
    doc.add('key', index)
    doc.add('title', title_link[1])
    doc.add('link', title_link[0])
    doc.add('summary', summart_conent[0])
    if len(summart_conent)>1:
        doc.add('content', summart_conent[1])
    else:
        doc.add('content', "网页失效")
    doc_list.append(doc)
    index+=1
    

    
#--------2.建立索引
inverted = {}   # 倒排索引记录词所在文档及词频
idf = {}         # 词的逆文档频率
id_doc = {}     # 文档与词的对应关系


doc_num = len(doc_list)     # 文档总数
stopwords = [line.strip() for line in open('./static/stopwords/stopwords.txt',encoding='UTF-8').readlines()]
ii=0
doc=doc_list[0]
for doc in doc_list:
    
    if ii%10==0:
        print("已处理"+str(ii/doc_num*100)+"%")
    ii+=1
    
    key = doc.get('key')
    # 正排
    id_doc[key] = doc
    #正文
    regStr = ".*?([\u4E00-\u9FA5]+).*?"
    content=doc.get('summary')+doc.get('content')+doc.get('title')
    s=""
    for i in re.findall(regStr, content):
        s+=i
    # 倒排
    # 搜索引擎分词
    jieba.add_word('常州大学')
    jieba.add_word('计算机学院')
    jieba.add_word('瞿秋白学院')
    term_list = list(jieba.cut(s,cut_all=False))   # 分词
    use_words=[]
    for i in term_list:
        if i not in stopwords:
            use_words.append(i)
    
    for t in use_words:
        if t in inverted:

            if key not in inverted[t]:
                inverted[t][key] = 1
            else:
                inverted[t][key] += 1
        else:
            inverted[t] = {key: 1}

for t in inverted:#总文档数/当前词出现的文档数
    idf[t] = math.log(doc_num / len(inverted[t]))

print("inverted terms:%d" % len(inverted))
print("index done")
#
##--------3.写文件
print("写倒排索引")

import json
with open('./static/json/inverted.json', 'w') as f:
    json.dump(inverted,f)

print("写idf")   
with open('./static/json/idf.json', 'w') as f:
    json.dump(idf,f)
