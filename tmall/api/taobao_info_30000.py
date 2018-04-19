#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: renxuewu
# 根据商品id获取商品详细信息及店家信息
# @Email:  seektolive@gmail.com
# @Date:   2018-04-18 15:59:57
# @Last Modified by:   renxuewu
# @Last Modified time: 2018-04-19 15:02:20

import mysql.connector
import logging
import logging.config
from urllib.parse import quote

import requests
import json
import headersobj
import proxy
import random
import time


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


from pyquery import PyQuery as pq

import headersobj
import proxy

proxies = proxy.get_random()
headers = headersobj.get_random_header()
'''
	打开浏览器
'''
# browser = webdriver.Chrome()
# wait = WebDriverWait(browser, 5)
# browser.maximize_window()

class Taobaoinfo:

	global proxies

	def init(self):
		logging.config.fileConfig('logconfig.ini')

	def get_conn(self):
		try:
			conn = mysql.connector.connect(user='root',password='imsbase',database='taobao')
			return conn
		except Exception as e:
			logging.debug(e)
	'''
	/**
	 * 查询需要采集的商品id列表
	 * keyword:查询关键字
	 * sorttype：排序
	 * pid：起始id
	 */
	'''
	def get_product_id(self,keyword,sorttype,versionstr,pid):
		# sql = 'SELECT nid,detail_url FROM galaxeed_product_list WHERE product_type="%s" AND sort_type="%s" AND iscollect="%s" AND id >= %s' %(keyword,sorttype,versionstr,pid)
		sql = 'SELECT id,nid,detail_url FROM galaxeed_product_list where id >30000 '
		try:
			con = self.get_conn()
			cur = con.cursor()
			cur.execute(sql)
			result = cur.fetchall()
			return result
		except Exception as e:
			logging.debug(sql,e)
		finally:
			cur.close()
			con.close()

	'''
	/**
	 * 根据商品详情url获取商品信息（销售信息和基本信息）
	 * url:商品url
	 */
	'''
	def get_product_info(self,pid,url):
		try:
			time.sleep(1)
			res = requests.get(url,headers=headers,proxies=proxies).text
			if res[:9] == 'mtopjsonp':
				data = json.loads(res[11:][:-1])
				selldata = json.loads(data['data']['apiStack'][0]['value'])
				if selldata:
					sellCount = selldata['item']['sellCount']
					self.insert_product_sell_info(pid,sellCount)
				else:
					return
			else:
				print('error',pid,res[:20])
				return
		except Exception as e:
			print('except',pid,res[:20])
			logging.debug('test',e)
			return

	'''
	/**
	 * 从结果中解析商品销售信息
	 * data:商品返回信息
	 */
	'''
	def parse_product_sell_info(data):
		pass
	'''
	/**
	 * 从结果中解析商品基本信息
	 * data:商品返回信息
	 */
	'''
	def parse_product_basic_info(data):
		pass
	'''
	/**
	 * 从结果中解析卖家基本信息
	 * data:返回信息
	 */
	'''
	def parse_product_seller_info(data):
		pass

	'''
	/**
	 * 保存商品销售信息
	 * product:商品销售信息
	 */
	'''
	def insert_product_sell_info(self,pid,sellcount):
		print(pid,sellcount)
		# tie_test
		sql = 'insert into tie_test(pid,sellcount) values(%s,%s)' %(pid,sellcount)
		try:
			con = self.get_conn()
			cur = con.cursor()
			cur.execute(sql)
			con.commit()
		except Exception as e:
			logging.debug(sql,e)
		finally:
			cur.close()
			con.close()
	'''
	/**
	 * 保存商品基本信息
	 * product:商品基本信息
	 */
	'''
	def insert_product_basic_info(product):
		pass
	'''
	/**
	 * 保存卖家基本信息
	 * seller:卖家基本信息
	 */
	'''
	def insert_seller_info(seller):
		pass

	# 开始爬取程序
	def spider(self):
		
		# 在运行之前配置属性
		keyword = '领带'
		sorttype = 'default'
		pid = '1'
		versionstr = '0'

		# 获取商品列表id
		pid_list = self.get_product_id(keyword,sorttype,versionstr,pid)
		
		# 循环根据商品id获取商品信息
		# https://acs.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?data=%7B%22itemNumId%22%3A%2210031645140%22%7D&qq-pf-to=pcqq.group
		if pid_list:
			for item in pid_list:
				# 生成url
				datastr = '{"itemNumId":"%s"}' %(item[1])
				data = quote(datastr)
				jsonstr= 'mtopjsonp%s' %(random.randint(1,9))
				# url = 'https://acs.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?data=%s' %(data)
				# url1 = 'https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?api=mtop.taobao.detail.getdetail&v=6.0&callback=%s&data=%s' %(jsonstr,data)
				# print(url1)
				# url2 = 'https://rate.taobao.com/detailCount.do?callback=jsonp173&itemId=%s' %(item[0])
				# print(url2)
				

				# url3 = 'https://detailskip.taobao.com/service/getData/1/p1/item/detail/sib.htm?itemId=%s&modules=dynStock,viewer,price,duty,xmpPromotion,delivery,activity,fqg,zjys,couponActivity,soldQuantity,originalPrice,tradeContract&callback=onSibRequestSuccess' %(item[0])

				if 'item.taobao' in item[2]:
					# url4 = 'https://item.taobao.com/item.htm?id=%s&ns=1&abbucket=0' %(item[0])
					url1 = 'https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?api=mtop.taobao.detail.getdetail&v=6.0&callback=%s&data=%s' %(jsonstr,data)
					print(item[0],'=',url1)
					try:
						self.get_product_info(item[1],url1)
					except Exception as e:
						proxies = proxy.get_random()
						continue
					
		else:
			return 
			# get_product_info(url)


if __name__ == '__main__':
	taobaoinfo = Taobaoinfo()
	taobaoinfo.init()
	taobaoinfo.spider()