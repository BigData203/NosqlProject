"""
使用缓存进行检索
"""

import operator
import math
import json
from top_k import *

with open('./static/json/idf.json', 'r') as f:
    idf = json.load(f)    #此时a是一个字典对象
with open('./static/json/inverted.json', 'r') as f:
    inverted = json.load(f)    #此时a是一个字典对象    

all_sorted=[]
length=0
li=[]
def p1(term_list,page):
        #2.获取inverted,idf            
        global all_sorted
        global length
        global li
        # 3.计算每篇文档的tf-idf,找出候选doc，只考虑了正文的一般性，忽略了文章中标题，首段落的特殊作用
        # TF−IDF=tf∗idf
        tf_idf = {}
        for term in term_list:#遍历分词列表
            if term in inverted:#分词存在于倒排索引中
                for doc_id, tf in inverted[term].items():#（取出doc_id文档号，tf次数）,不是词频，没有除文档总次数
                    if doc_id in tf_idf:
                        tf_idf[doc_id] += (1 + math.log(tf)) * idf[term]#（tf次数，具体词与具体文档的关系），当前文档与词的联系，（具体词idf[term]与全部文档的关系）词出现的逆文档频率
                    else:
                        tf_idf[doc_id] = (1 + math.log(tf)) * idf[term]
            
        length=len(tf_idf)             

        #4.全排序

        all_sorted = sorted(tf_idf.items(), key=operator.itemgetter(1), reverse=True)
        all_sorted=[list(i)  for i in all_sorted]

        
        #考虑文章中标题，首段落的特殊作用，进行修正，加一个bias
         #标题，摘要加大权值
        title=[]
        summary=[]
        for i in all_sorted[:10]:
            print(i[0])
            texts=open('./static/doc/'+str(i[0])+".txt",encoding="utf-8").read()
            title.append(texts.split()[1])
            summary.append(texts.split('\n\n\n',1)[1].split('\n\n\n',1)[0])
        for index_title in range(len(title)):
            for term in term_list:
                if term in title[index_title]:#遍历标题
                    all_sorted[:30][index_title][1]+=idf[term]*15
                if term in summary[index_title]:#遍历摘要
                    all_sorted[:30][index_title][1]+=idf[term]*5
                    
        all_sorted[:30]=sorted(all_sorted[:30],key=lambda x: x[1],reverse=True)
        all_sorted=[tuple(i)  for i in all_sorted]#转回元组
         
        
def s(term_list,page):
    page-=1
    if page<1:
        p1(term_list,page)
        sorted_doc=all_sorted[page*10:page*10+10]#取前10
    else:
        sorted_doc=all_sorted[page*10:page*10+10]#取前10
        
   
    
    #5.得到文档ID
    doc_id=[]
    for i in sorted_doc:
        doc_id.append(i[0])
    
    #6.获得文章  
    texts=[]
    for file in doc_id:
        texts.append(open('./static/doc/'+file+".txt",encoding="utf-8").read())

    doc_list = []
    res=[]
    index=0
    
    for i in texts:
        a=i.split('\n\n\n',1)
        summart_conent=a[1].split('\n\n\n',1)
        title_link=a[0].split()
        doc={}
        doc['key']=doc_id[index]
        doc['title']=title_link[1]
        doc['link']=title_link[0]
        doc['summary']=summart_conent[0]
        if len(summart_conent)>1:
            doc['content']=summart_conent[1]
        else:
            doc['content']="网页失效"
        doc_list.append(doc)
        print(index)
        index+=1
        
        res.append(doc)
    return res,length

   

   
