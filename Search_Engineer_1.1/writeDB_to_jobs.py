# -*- coding: utf-8 -*-
"""
写数据库
"""
from pymongo import *
import json

    
class Json2Mongo2(object):
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

    # 写入数据库
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


    # 从数据库读取
    def read_datebase(self ,word):
        scene_flow=[]
        for i in word:
            try:
                myquery = {"name": i} # 查询条件
                scene_flow.append(self.collection.find(myquery))
            except Exception as e:
                print(e)
        
        return scene_flow


import jieba
if __name__ == '__main__':
   jm2 = Json2Mongo2()
   jm2.write_database()
   query="我在常州大学大数据学院学习"
   word= list(jieba.cut_for_search(query.replace(" " ,"")))
   suo=jm2.read_datebase(word)
   suo1={}
   for x in suo:
       for j in x:
           suo1[list(j.items())[1][1]]=list(j.items())[2][1]
