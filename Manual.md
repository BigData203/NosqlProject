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
# Flask框架
运行搜索引擎
----
预加载idf文件

    with open('./static/json/idf.json', 'r') as f:#预加载idf文件
        idf = json.load(f)    

设置检索首页的路由

    @app.route("/", methods=['POST', 'GET'])#设置检索首页的路由
    def main():
        if request.method == 'POST' and request.form.get('query'):
            query = request.form['query']
            print(query)
            return redirect(url_for('search', query=query))

        return render_template('kuaisou.html')

设置检索页的路由

    @app.route("/q/<query>", methods=['POST', 'GET'])#设置检索页的路由
    def search(query):
        start=time.time()#开始计时
        page, per_page, offset = get_page_args(page_parameter='page',
                                               per_page_parameter='per_page')
        terms = [i for i in jieba.cut_for_search(query.replace(" " ,"")) if len(i)>1 and i in idf]#处理检索式
        terms.sort(key = lambda i:len(i),reverse=True)
        #获得摘要等信息    
        alll,length= getsummary(terms,page)#page=0,返回0-9，page=1,返回10-19
        result = highlight(alll, terms)
        #实现分页
        pagination = Pagination(page=page, per_page=10, total=length-1,
                                css_framework='bootstrap4')
        a=time.time()-start#结束计时
        #将参数返回给网页
        return render_template('search.html', docs=result, value=query, length=length,pagination=pagination,t=str('%.3f'%a))

对关键词进行高亮
    
    def highlight(alll, terms):
        result = []
        titles=[]
        contents=[]

        for doc in alll[0]:#标题高亮
            for term in terms:
                doc=doc.replace(term, '<em><font color="red">{}</font></em>'.format(term))
            titles.append(doc)
        i=0
        for doc in alll[1]:#正文高亮
            print(i)
            i+=1
            if doc != None:
                for term in terms:
                    doc=doc.replace(term, '<em><font color="red">{}</font></em>'.format(term))
            else:
                doc="无法查询"
            contents.append(doc+"...")
        for i in range(len(titles)):
            result.append([alll[2][i],contents[i],titles[i]])
        return result

# 爬虫
爬虫
----
网页去重

    class UrlManager(object):
        def __init__(self):
            self.new_urls = set()#待爬取url集合
            self.old_urls = set()#以爬取url集合

        def add_new_url(self, begin_url):
            if begin_url is None:
                return
            if begin_url in self.new_urls or begin_url in self.old_urls:
                return
            self.new_urls.add(begin_url)

        def has_new_url(self):
            return len(self.new_urls) != 0

        def get_new_url(self):#取出一个url
            new_url = self.new_urls.pop()
            self.old_urls.add(new_url)#添加至以爬取url集合中
            return new_url

        def add_new_urls(self, new_urls):
            if new_urls is None or len(new_urls) == 0:
                return
            for url in new_urls:
                self.add_new_url(url)

下载器

    class HtmlDownloader(object):

        def download(self, new_url):
            #防止证书不受信任，但是忽略仍可继续访问，直接信任所有Https的安全证书
            ssl._create_default_https_context = ssl._create_unverified_context
            response = request.urlopen(new_url)
            print("请求返回码：%d" % response.getcode())
            if response.getcode() != 200:
                return None
            return response.read()

解析器

    class HtmlParser(object):

        def parse(self, new_url, html_content):
            if html_content is None or new_url is None:
                return
            soup = BeautifulSoup(html_content, 'html.parser')
            new_urls = self._get_new_urls(new_url, soup)
            new_data = self._get_new_data(new_url, soup)
            return new_urls,new_data

        def _get_new_urls(self, new_url, soup):#按照广度优先搜索策略进行链接提取
            full_urls = set()
            links = soup.find_all("a", href=re.compile(r"/item/"))
            for link in links:
                url_href = link["href"]
                full_url_href = parse.urljoin(new_url, url_href)#网页地址组合，把相对地址转化为绝对地址"http://www.google.com/1/aaa.html"+"bbbb.html"='http://www.google.com/1/bbbb.html'
                full_urls.add(full_url_href)
            return full_urls

        def _get_new_data(self, new_url, soup):#提取网页信息
            res_data = {"url": new_url}
            # 获取title class="lemmaWgt-lemmaTitle-title"
            title = soup.find("dd", class_="lemmaWgt-lemmaTitle-title").find("h1").get_text()
            res_data["title"] = title
            # 获取摘要  class = "lemma-summary"
            summary = soup.find("div", class_="lemma-summary").get_text()
            res_data["summary"] = summary
            #正文 
            content = soup.find("div", class_="main-content").get_text()
            text = re.sub(r'\n+','',content)  # 换行改成句号（标题段无句号的情况）
            res_data["content"] = text
            return res_data
            
 输出部分
 
    class Outputer(object):
        def __init__(self):
            self.datas = []

        def collect_data(self, new_data):
            if new_data is None:
                return
            self.datas.append(new_data)

        def output_txt(self):#将网页以TXT格式输出
            for i in range(all_nums):
                name = r"./static/doc/" + str(i+start) + ".txt"
                with open(name, 'w', encoding='utf-8') as fout:
                    data = self.datas[i]
                    fout.write(data['url']+"\r\n")
                    fout.write(data['title']+"\r\n")
                    fout.write(data['summary']+"\r\n")
                    fout.write(data['content']+"\r\n")   
                    
爬虫整合模块

    class SpiderMain(object):
        def __init__(self):
            self.urls = UrlManager()
            self.downloader = HtmlDownloader()
            self.parser = HtmlParser()
            self.outputer = Outputer()

        #抓取函数：给定起始url
        def craw(self, begin_url):
            count = 1
            self.urls.add_new_urls(begin_url)
            while self.urls.has_new_url():#判断当前url集合中还有url
                try:
                    if count > all_nums:#爬取指定数量网页
                        break
                    new_url = self.urls.get_new_url()#取出一个url
                    print("craw %d : %s" % (count, new_url))
                    html_content = self.downloader.download(new_url)#进行爬取
                    new_urls, new_data = self.parser.parse(new_url, html_content)#网页解析
                    self.urls.add_new_urls(new_urls)
                    self.outputer.collect_data(new_data)
                    count += 1
                except BaseException as e:#对所有异常进行抛出
                    print(e)
                    print("craw fail")

            self.outputer.output_txt()  
            
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
