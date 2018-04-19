#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: renxuewu
# @Email:  seektolive@gmail.com
# @Date:   2018-04-16 13:47:17
# @Last Modified by:   renxuewu
# @Last Modified time: 2018-04-16 13:47:35
import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq   #获取整个网页的源代码

from config import *   #可引用congif的所有变量
import pymongo
import pymysql

# client=pymongo.MongoClient(MONGO_URL)
# db = client[MONGO_DB]

#  按综合排序 100页


# 打开淘宝链接，输入‘美食’，搜索
# 自动翻页：先得到总页数，再转到 _ 页，确定
#

# browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)
# browser =webdriver.Chrome()
browser = webdriver.Firefox()
wait = WebDriverWait(browser,10)

def search():
    print('正在搜索...')
    try:
        browser.get('https://www.taobao.com')  #用这个网页'https://s.taobao.com'，无法输入keywords
        input=wait.until(
             EC.presence_of_element_located((By.CSS_SELECTOR,'#q'))  #打开淘宝，右击查看元素，定位到搜索框，选择对应代码，复制-CSS选择器，其实就是‘#q’。
        )
        submit=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_TSearchForm > div.search-button > button')))
        input.send_keys(KEYWORD)   #模拟操作，输入内容
        submit.click() #点击提交
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.total')))  #页数
        return total.text
    except TimeoutException :
        return search()

# 翻页
def next_page(page_number):
    print('正在翻页',page_number)
    try:
        input = wait.until(
            # 输入框
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input'))  # 打开淘宝，右击查看元素，定位到搜索框，选择对应代码，复制-CSS选择器，其实就是‘#q’。
        )
        # 搜索按钮
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))  #未修改
        input.clear()
        input.send_keys(page_number)  # 模拟操作，输入页码
        submit.click()
        #判断翻页是否成功，找到高亮页码数，由数子判断
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR ,'#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number)))
        get_products()
    except TimeoutException :
        next_page(page_number)

# 解析，获取每页的商品并输出
def get_products():
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'#mainsrp-itemlist .items .item'))) #加载所有宝贝
    html=browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            # 'picture':item.find('.pic .img').attr('src'),#用find去获取内部元素，选择器是 pic，img，用attr获取属性
            'image': item.find('.pic .img').attr('data-src'),  # 用find去获取内部元素，选择器是 pic，img，用attr获取属性
            'shop_id': item.find('.shop').find('a').attr('data-userid'), # 店铺 id
            'data_id': item.find('.shop').find('a').attr('data-nid'),  # 商品 id
            'link': item.find('.pic-box-inner').find('.pic').find('a').attr['href'],
            'price':item.find('.price').text()[1:-3],  # 用text获取内容
            'deal':item.find('.deal-cnt').text()[:-3],
            'title':item.find('.title').text().replace(' ',''),
            'shop':item.find('.shop').text(),
            'location':item.find('.location').text()
        }
        # print(product)
        # print(product['location'])
        save_to_mysql(product)
'''
def main():
    try:
        # search()
        total=search()  # 此时 total = ‘共 100 页，’
        total=int(re.compile('(\d+)').search(total).group(1)) # 用正则表达式提取数字100
        # print(total)
        for i in range(2,total+1):
            next_page(i)
    except Exception:
        print('出错啦')
    finally:  #  不管有没有异常，都要执行此操作
        browser.close()  # 关浏览器
'''

def main():
    total=search()
    total=int(re.compile('(\d+)').search(total).group(1))
    for i in range(2,total+1):
        next_page(i)#显示当前爬取网页的页数
        print ('搞定%d'%i)

def save_to_mysql(product):
    # print(product['location'])
    #,use_unicode = False
    try:
        conn = pymysql.connect(host='localhost', user='root', passwd=' ', db='test1', port=3306,charset='utf8' )
        cur = conn.cursor()  # 创建一个游标对象
        sql = """INSERT INTO women_clothes_zonghe VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cur.execute(sql, (product['shop_id'],product['shop'], product['link'],product['data_id'], product['title'], product['price'],  product['location'],product['deal'],product['image']))
        # cur.execute(sql)
        print('- - - - - 数据保存成功 - - - - -')
        cur.close()
        conn.commit()
        conn.close()  # 关闭数据
    except pymysql.Error as e:
        print(e)

if __name__=='__main__':
   # 连接数据库
   conn = pymysql.connect(host='localhost', user='root', passwd=' ', db='test1', port=3306,charset="utf8")
   cur = conn.cursor()  # 创建一个游标对象
   cur.execute("DROP TABLE IF EXISTS women_clothes_zonghe")  # 如果表存在则删除
   # 创建表sql语句
   sqlc = """CREATE TABLE women_clothes_zonghe(
       shop_id VARCHAR(500),
       shop VARCHAR(500),
       link VARCHAR(1000),
       data_id varchar(100),
       title VARCHAR(1000),
       price VARCHAR(500),
       location VARCHAR(500),
       deal VARCHAR(500),
       image VARCHAR(1000)
   )"""
   cur.execute(sqlc)  # 执行创建数据表操作
   main()