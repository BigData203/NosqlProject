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
