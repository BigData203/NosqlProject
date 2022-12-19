# -*- coding: utf-8 -*-
"""
写数据库
"""
from pymongo import *
import json

class Json2Mongo(object):
    def __init__(self):
        self.host = 'localhost'
        self.port = 27017
        # 创建mongodb客户端
        self.client = MongoClient(self.host, self.port)
        # 创建数据库dialog
        self.db = self.client.SearchDemo
        # 创建集合scene
        self.collection = self.db.idf
        # 读取idf.json
        self.json_data = json.load(open('./static/json/idf.json'))
        self.lenj = len(self.json_data)

    # 写入数据库
    def write_database(self):   
        index=0
        for i in self.json_data:
            if index%100==0:
                print(index/self.lenj*100)
            index+=1
            data = {
                "name": i,
                "idf": self.json_data[i]
            }
            try:
                myquery = {"name": i}  # 查询条件
                self.collection.update(myquery, data, upsert=True)
            except Exception as e:
                print(e)

    # 从数据库读取
    def read_datebase(self ,word):
        scene_flow=[]
        for i in word:
            try:
                myquery = {"name": i} # 查询条件
                scene_flow.append(self.collection.find(myquery))
            except Exception as e:
                print (e)
        
        return scene_flow
    

import jieba
if __name__ == '__main__':
   jm = Json2Mongo()
   # jm.write_database()
   query="我在常州大学大数据学院学习"
   word= list(jieba.cut_for_search(query.replace(" " ,"")))
   idf=jm.read_datebase(word)
   idf1={}
   for x in idf:
       for j in x:
           idf1[list(j.items())[1][1]] = list(j.items())[2][1]
   print(idf1)
