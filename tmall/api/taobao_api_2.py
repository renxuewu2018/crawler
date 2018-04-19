#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: renxuewu
# 根据关键字获取商品列表信息
# 使用说明
# 1. 见表 tablename  并把表名设置好
# 2. 如果单独根据关键字和某一排序方法采集，需要设置querykey,sort_type这连个字段，并在main
# 方法中调用get_product_list方法
# 3. 如果批量采集某些关键字和不同排名下的商品信息，需要调用get_product_list_all 并设置其内的keywordlist
# 关键字
# 4. 如果针对某个关键字定期采集，需要设置iscollect  采集版本以便区分
# @Email:  seektolive@gmail.com
# @Date:   2018-04-16 15:07:08
# @Last Modified by:   renxuewu
# @Last Modified time: 2018-04-18 15:06:31

import requests
import json
import mysql.connector
import time
import random

import headersobj
import proxy

import logging
import logging.config
logging.config.fileConfig('logconfig.ini')


# 保存数据
conn = mysql.connector.connect(user='root',password='imsbase',database='taobao')
cursor = conn.cursor()


# 更新代理
proxies = {"http":''} 
headers = headersobj.get_random_header()

currentPage = 1
pageSize = 44
# 1、根据关键字和排序信息查询商品列表
def get_product_list(keys,sorttype,num=0):
	global proxies,headers,currentPage,pageSize
	# 获取商品列表信息的url
	rooturl = 'https://s.taobao.com/search?ajax=true&callback=%s&tab=all&style=list&q=%s&sort=%s&s=%d' %(get_random(),keys,sorttype,num)
	logging.info(rooturl)
	print(rooturl)

	try:
		res = requests.get(rooturl,proxies=proxies,headers=headers).text
		# res = requests.get(rooturl).text

		jsonp_str = res[2:7]
		# 判断是否返回json格式的结果，如果结果正常，继续解析执行，如果异常更换ip重新访问
		if jsonp_str == 'jsonp':
			json_str = res[12:][:-2]
			data = json.loads(json_str)
			totalPage = data['mods']['pager']['data']['totalPage']# 总页数
			currentPage = data['mods']['pager']['data']['currentPage']# 当前页
			pageSize = data['mods']['pager']['data']['pageSize']# 每页显示数量
			
			# 解析并保存当前页的数据
			products = data['mods']['itemlist']['data']['auctions']
			insert_product_list(products,currentPage,keys,sorttype)
			# 判断是否到最后一页
			print(currentPage,':',totalPage)
			if currentPage==totalPage:
				return
			else:
				# 跳转到下一页
				get_product_list(keys,sorttype,currentPage*pageSize)
		else:
			# print(jsonp_str)
			# 随机更换ip 继续访问
			# IndentationError			
			proxies['http'] = proxy.get_random_proxy()
			headers = headersobj.get_random_header()
			callback('1',currentPage,pageSize,keys,sorttype)
	except Exception as e:
		# raise e
		proxies['http'] = proxy.get_random_proxy()
		headers = headersobj.get_random_header()
		logging.debug(e)
		print(e)
		callback('2',currentPage,pageSize,keys,sorttype)
	except TimeoutError as t:
		# raise t
		proxies['http'] = proxy.get_random_proxy()
		headers = headersobj.get_random_header()
		logging.debug(t)
		callback(currentPage,pageSize,keys,sorttype)
		
# 如果出现问题变化id后再次访问url
def callback_old(num,currentPageint,pageSize,keys,sorttype):
	print('callback',num,currentPage,pageSize)
	if currentPageint==1:
		get_product_list(keys,sorttype)
	else:
		get_product_list(keys,sorttype,(currentPageint)*pageSize)

# 如果出现问题变化id后再次访问url
# update 添加容错机制，如果一个连接连续几次都访问不成功，则放弃
dict = {}
errortimes = 3 # 容错次数
def callback(num,currentPageint,pageSize,keys,sorttype):
	key = str(currentPageint)+sorttype
	if key in dict:
		dict[key] = dict[key] + 1
	else:
		dict[key] = 1
	
	if dict[key] > errortimes:
		get_product_list(keys,sorttype,(currentPageint+1)*pageSize)
	else:	
		print('callback:',dict[key],num,currentPageint,pageSize)
		logging.info('callback:',dict[key],num,currentPageint,pageSize)
		if currentPageint==1:
			get_product_list(keys,sorttype)
		else:
			get_product_list(keys,sorttype,(currentPageint)*pageSize)

# 判断是否有此属性，因为有的数据没有此属性，在获取的时候会报错
# python2中用has_key 判断，python3中用in判断，obj中用hasattr判断
def is_exiaxt(att):
	if 'view_sales' in att:
		return att['view_sales']
	else:
		return '0人付款'
# 生成随机回调函数
def get_random():
	num = random.randint(1000,9999)
	return 'jsonp%d' %(num)

product_ids = []

# 2、将采集到的商品列表中的信息插入到数据库中
def insert_product_list(products,currentPageint,keys,sorttype):
	global rank
	product_list = []
	for index,product in enumerate(products):
		collect_time = get_current_time()
		releasestr = get_release(product['nid'])
		view_sales = is_exiaxt(product)

		# 排名
		ranking = get_ranking(index,currentPageint)

		product_touple = (product['nid'],product['category'],product['title'],product['raw_title'],get_url(product['detail_url']),
			product['view_price'],product['view_fee'],product['item_loc'],view_sales[:-3],product['comment_count'] if product['comment_count'] else 0,
			product['user_id'],product['nick'],get_url(product['shopLink']),get_url(product['comment_url']),product['pid'],
			'0',collect_time,collect_time,keys,sorttype,releasestr,currentPageint,ranking)
		product_list.append(product_touple)

	rank = currentPageint*pageSize
	sql = 'insert into '+tablename+'(nid,category,title,raw_title,detail_url,view_price,view_fee,item_loc,view_sales,comment_count,\
		user_id,nick,shopLink,comment_url,pid,iscollect,createtime,updatetime,product_type,sort_type,releasestr,currentpage,ranking)\
		values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
	# print(sql)
	cursor.executemany(sql,product_list)
	conn.commit()

rank = 0
# 计算排名
def get_ranking(index,currentPageint):
	global rank
	return  rank + (index+1)


#判断是否之前已经采集过，如果采集过，版本号++
def get_release(nid):
	sql = 'select nid,releasestr from %s  where  nid="%s" order by releasestr desc' %(tablename,nid)
	cursor.execute(sql)
	result = cursor.fetchall()
	if len(result) > 0:
		return int(result[0][1])+1
	else:
		return 1


# 判断连接中是否有https
def get_url(url):
	if 'https' in url:
		return url
	else:
		return 'https:%s' %(url)

'''
	获取数据采集时间
'''
def get_current_time():
	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

# 关闭数据库
def close_db():
	cursor.close()
	conn.close()


tablename = 'galaxeed_product_list' # 插入表
querykey = '领带'  # 查询关键字
sort_type = 'defalt'  # 排序方法
iscollect = '0' # 采集版本  2018-04-18 第一次采集

# 批量运行 price-asc
def get_product_list_all():
	orderbylist = ['default','renqi-desc','sale-desc','price-asc','price-desc','total-asc','total-desc']
	keywordlist = ['领带 云锦']
	# orderbylist = ['sale']
	for key in keywordlist:
		for item in orderbylist:
			get_product_list(key,item)



if __name__ == '__main__':
	start = time.clock()

	# 关键字+排序单独执行，需要设置querykey,sort_type字段
	# get_product_list(querykey,sort_type)
	
	# 全部执行
	get_product_list_all()
	close_db()
	end = time.clock()
	print('running time:%s seconds' %(end-start))

