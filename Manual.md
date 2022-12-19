# 数据库设计
实现数据的导入以及搜索模块
----
导入模块from pymongo import *
实现数据库的连接并读取已经爬取的json数据

    def __init__(self):
        self.host = 'localhost'
        self.port = 27017
        # 创建mongodb客户端
        self.client = MongoClient(self.host, self.port)
        # 创建数据库dialog
        self.db = self.client.SearchDemo
        # 创建集合scene
        self.collection = self.db.jobs
        # 读取inverted.json
        self.json_data = json.load(open('./static/json/inverted.json'))
        self.lenj = len(self.json_data)
        
通过index去判断现在录入到多少了
通过self.collection.update去录入数据（upsert=True不存在则插入，存在则更新）
异常则抛出

     def write_database(self):   
            index=0
            for i in self.json_data:
                if index%100==0:
                    print(index/self.lenj*100)
                index += 1
                data = {
                    "name": i,
                    "content": self.json_data[i]
                }
                try:
                    myquery = {"name": i}  # 查询条件
                    self.collection.update(myquery, data, upsert=True)  # upsert=True不存在则插入，存在则更新
                except Exception as e:
                    print(e)
                    
通过传入的word去数据库搜索异常则抛出
返回一个列表
这里传入的word需要通过jieba模块的函数去切分。

       jm2.write_database()
       query="我在常州大学大数据学院学习"
       
       def read_datebase(self ,word):
        scene_flow=[]
        for i in word:
            try:
                myquery = {"name": i} # 查询条件
                scene_flow.append(self.collection.find(myquery))
            except Exception as e:
                print(e)
        return scene_flow
        
在DB_search模块上我们基于search模块上进行修改
通过数据库模块的read_datebase模块进行读取数据库数据

    idf1=jm.read_datebase(term_list)
    suo1=jm2.read_datebase(term_list)
    
然后jieba提取出的词的idf和inverted存储在字典里

    for x in idf1:
        for j in x:
            idf[list(j.items())[1][1]]=list(j.items())[2][1]
    for x in suo1:
        for j in x:
            inverted[list(j.items())[1][1]]=list(j.items())[2][1]

# 倒排索引算法
建倒排索引
----
读取文件

    import os
    import re
    texts=[]

    fname=os.listdir('./static/doc')
    fname.sort(key= lambda x:int(x[:-4]))
    for file in fname:
        texts.append(open('./static/doc/'+file,encoding="utf-8").read())
        
获取文档对应部分的内容

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
        
建立索引
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
    
 写文件
 
    print("写倒排索引")

    import json
    with open('./static/json/inverted.json', 'w') as f:
        json.dump(inverted,f)

    print("写idf")   
    with open('./static/json/idf.json', 'w') as f:
        json.dump(idf,f)
