
执行文件顺序是
1.Spider_2.py进行爬取网页并分析
2.index.py生成倒排索引，idf文件
如使用数据库要运行writeDB
3.app.py运行搜索引擎
4.在默认浏览器输入 http://localhost:8080/ 进行检索

若要使用数据库
1.writeDB.py写倒排索引与idf(时间较长)
2.可以在summary.py切换from DB_search import s使用数据库 

注意：
1.还需要停用词是stopwords.txt
2.pip install xlrd==1.2.0
3.在新版python3.9中，windows中使用的更新删除了getiterator方法,所以我们老版本的xIrd库调用getiterator方法时会报错。AttributeError:
ELementTree' object has no attribute getiterator'
