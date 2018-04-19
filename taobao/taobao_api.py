#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: renxuewu
# @Email:  seektolive@gmail.com
# @Date:   2018-04-16 15:07:08
# @Last Modified by:   renxuewu
# @Last Modified time: 2018-04-16 23:27:54

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

import requests
import json
import mysql.connector
import time


browser = webdriver.Chrome()
wait = WebDriverWait(browser, 5)
browser.maximize_window()
querykey = '领带 云锦'

def main():
	rooturl = 'https://s.taobao.com/search?ajax=true&callback=jsonp1559&q='+querykey+'&tab=all&style=list'
	url = 'https://s.taobao.com/search?ajax=true&callback=jsonp1559&q='+querykey+'&tab=all&style=list&s='
	browser.get(rooturl)
	res = browser.page_source
	json_str = res[133:][:-22]
	products = json.loads(json_str)
	pagenum = products['mods']['pager']['data']['totalPage']
	# print(products['mods']['sortbar']['data']['price']['rank'])
	for i in range(0,int(pagenum)):
		url1 =url + str(i*44)
		print(url1)
		time.sleep(1)
		get_product_list(url1)

product_ids = []
def get_product_list1(url):
	try:
		browser.get(url)
		res = browser.page_source
		res_json_str = res[133:][:-22]
		res_json = json.loads(res_json_str)
		products = res_json['mods']['itemlist']['data']['auctions']
		for product in products:
			productid = product['nid']
			product_ids.append(product)
			print(productid)
			save(product)
	except Exception as e:
		get_product_list(url)


def get_product_list(url):
	browser.get(url)
	res = browser.page_source
	res_json_str = res[133:][:-22]
	res_json = json.loads(res_json_str)
	products = res_json['mods']['itemlist']['data']['auctions']
	for product in products:
		productid = product['nid']
		product_ids.append(product)
		print(productid)
		save(product)
# 保存数据
conn = mysql.connector.connect(user='root',password='imsbase',database='taobao')
cursor = conn.cursor()
def save(product):
	sql = 'insert into product_list(taobaoid,querykey,createtime) values(%s,%s,%s)'
	cursor.execute(sql,(product['nid'],querykey,get_current_time()))
	conn.commit()

'''
	获取数据采集时间
'''
def get_current_time():
	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

# 关闭数据库
def close_db():
	cursor.close()
	conn.close()
	browser.close()

if __name__ == '__main__':
	start = time.clock()
	main()
	close_db()
	end = time.clock()
	print('running time:%s seconds' %(end-start))
	# main()
