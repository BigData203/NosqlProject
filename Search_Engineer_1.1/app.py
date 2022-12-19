# coding:utf-8
from flask import Flask, request, render_template, redirect, url_for
import jieba
from flask_bootstrap import Bootstrap
from summary import  getsummary
from flask_paginate import Pagination, get_page_args
import json
import time
app = Flask(__name__, static_url_path='')
bootstrap = Bootstrap(app)
with open('./static/json/idf.json', 'r') as f:#预加载idf文件
    idf = json.load(f)    
    
@app.route("/", methods=['POST', 'GET'])#设置检索首页的路由
def main():
    if request.method == 'POST' and request.form.get('query'):
        query = request.form['query']
        print(query)
        return redirect(url_for('search', query=query))
    
    return render_template('kuaisou.html')


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

#对关键词进行高亮
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


if __name__ == "__main__":
    jieba.add_word('常州大学')#jieba词典扩充
    jieba.add_word('大数据')
    app.run(host='localhost', port=8080, debug=True)#http://localhost:8080/
