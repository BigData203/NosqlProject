# -*- coding: utf-8 -*-

import jieba
import re
import os
from sklearn.feature_extraction.text import TfidfTransformer,CountVectorizer
from search import s
# from DB_search import s
from top_k import top_k

class MyTfIdf:
    def __init__(self, s):#初始化参数，
        self.s = [s]

    def fenci(self, v):#返回字符串"搜索引擎 包含 了 ..."
        v = re.sub("[\：\·\—\，\。\“ \”]", "", v)#去标点符号
        words = [word for word in jieba.cut_for_search(v)]
        words = [i for i in words if i not in ('',' ','\n')]
        string = ' '.join(words)
        return string

    def getTfIdfValues(self):#求每个词的tfidf
        if self.s:
            cut_s = list()
            for v in self.s:
                cut_s.append(self.fenci(v))
            v = CountVectorizer()
            t = TfidfTransformer()
            tf_idf = t.fit_transform(v.fit_transform(cut_s))
            word = v.get_feature_names()
            weight = tf_idf.toarray()
            tf_idfDict = {}#单词对应权值
            for i in range(len(weight)):#文档
                for j in range(len(word)):#文档中的单词
                    getWord = word[j]
                    getValue = weight[i][j]
                    if getValue != 0:
                        if tf_idfDict.__contains__(getWord):
                            tf_idfDict[getWord] += float(getValue)
                        else:
                            tf_idfDict.update({getWord: getValue})
            return tf_idfDict


class CreateAbstract:#摘要类实现
    def __init__(self, data, kv):
        self.data = data
        self.tfidf = MyTfIdf(data).getTfIdfValues()
        self.kv = kv

    def s_match(self, s, s1):#找到每个词的位置
        loc = list()
        l_s = len(s)
        l_s1 = len(s1)
        for i in range(l_s - l_s1 + 1):#蛮力法
            index = i
            for j in range(l_s1):
                if s[index] == s1[j]:
                    index += 1
                else:
                    break
            if index - i == l_s1:
                loc.append(i)
        return loc

    def getShingle(self, loclist):# 拆分得到滑动窗口信息
        txtLine = list()# 切片文本
        for l in loclist:
            txtLine.append(self.data[l:l + self.kv])#切片操作s[i:i+k]
        # print('得到窗口信息', txtLine)
        return txtLine

    

    def getLoc(self, _keywords):
        a = []
        for k in _keywords:
            s = [self.data[i:i + len(k)] for i in range(len(self.data) - len(k) + 1)]
           
            for i in range(len(s)):
                if s[i] == k:
                    a.append(i)
        return a
    
    # 给生成的每段窗口打分
    def getScore(self, tfidfV, txtline, keywords):# tfidf的值，生成的窗口信息,关键词列表
        score = dict()
        for i, v in enumerate(txtline):
            if not score.get(i):
                score[i] = 0  # 每一段初始化是0
            for keyw in keywords:# 对于每个关键词
                if keyw in v:
                    if keyw in tfidfV:
                        score[i] += v.count(keyw)*tfidfV[keyw]
                        
        a=[list(i) for i in score.items()]
        sortedDic=top_k(a,min(len(a),10))
        # print('窗口得分', sortedDic)
        return sortedDic
    
    def getResult(self, term_list):
        _keywords = term_list
        tfidfV = self.tfidf
#        print('tfidf的分数', tfidfV)
        loclist = self.getLoc(_keywords)
        if loclist==[]:
            return None
        txtline = self.getShingle(loclist)
        scores = self.getScore(tfidfV, txtline, _keywords)
        maxShingle = txtline[scores[0][0]]
        
        return maxShingle

#生成摘要
def getsummary(term_list,page):
    a,length = s(term_list,page)#返回文档列表嵌套字典
    contents=[]
    titles=[]
    links=[]
    for i in a:
        contents.append(i['content'])
        titles.append(i['title'])
        links.append(i['link'])
    index=0
    summ=[]
    
    for data in contents:
        if index<10:
            tmp=CreateAbstract(data, 120).getResult(term_list)
            summ.append(tmp)
        else:
            summ.append("暂无生成")
        index+=1
    alll=[titles,summ,links]
    print(length)
    return alll,length


#if __name__ == "__main__":
#    kw="瞿秋白"
#    kw="大数据"
#    jieba.add_word('常州大学')
#    kw=list(jieba.cut_for_search(kw))
#    alll,length= getsummary( kw,1)