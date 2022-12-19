# -*- coding: utf-8 -*-
"""
爬虫
"""
all_nums=1
start=0#用于文件命名的全局变量

#网页去重
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
            
            
import ssl
from urllib import request,parse

#下载器
class HtmlDownloader(object):

    def download(self, new_url):
        #防止证书不受信任，但是忽略仍可继续访问，直接信任所有Https的安全证书
        ssl._create_default_https_context = ssl._create_unverified_context
        response = request.urlopen(new_url)
        print("请求返回码：%d" % response.getcode())
        if response.getcode() != 200:
            return None
        return response.read()
    
import re
from bs4 import BeautifulSoup

#解析器
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
    
#输出部分
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


#爬虫整合模块
class SpiderMain(object):
    def __init__(self):
        self.urls = UrlManager()
        self.downloader = HtmlDownloader()
        self.parser = HtmlParser()
        self.outputer = Outputer()
    
    #抓取函数：给定起始url
    def craw(self, begin_url):
        count = 1
        self.urls.add_new_url(begin_url)
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


if __name__ == "__main__":
#    root_url = "https://www.cczu.edu.cn/main.htm"
    root_url = "https://baike.baidu.com/item/%E5%B8%B8%E5%B7%9E%E5%A4%A7%E5%AD%A6"
    obj_spider = SpiderMain()
    obj_spider.craw(root_url)