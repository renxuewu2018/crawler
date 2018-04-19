#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 采集淘宝和天猫商品属性（包括通用属性和特有属性）
# @Author: renxuewu
# @Email:  seektolive@gmail.com
# @Date:   2018-04-17 09:52:26
# @Last Modified by:   renxuewu
# @Last Modified time: 2018-04-17 14:06:07

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from pyquery import PyQuery as pq
import re,time,random
import mysql.connector
from lxml import etree
import proxy


'''
	打开浏览器
'''
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 5)
browser.maximize_window()

def change_proxy():
	chromeOptions = webdriver.ChromeOptions()
	# 设置代理
	proxy_para = '--proxy-server=http://'+proxy.get_random_proxy()
	chromeOptions.add_argument(proxy_para)
	# 一定要注意，=两边不能有空格，不能是这样--proxy-server = http://202.20.16.82:10152
	browser = webdriver.Chrome(chrome_options = chromeOptions)

'''
	连接数据库
'''
conn = mysql.connector.connect(
	user='root', password='imsbase', database='spider')
cursor = conn.cursor()

# 根据开始id和结束id、排序类型 获取id列表
def get_product_ids(startid,endid,sorttype):
	get_ids_sql = 'select t.id,t.queryKeyword,t.detailedInfoUrl from taobao_productlist t where  \
	t.id >='+str(startid)+' and t.id <'+str(endid)
	# +' and t.orderby="'+sorttype+'"'
	cursor.execute(get_ids_sql)
	result = cursor.fetchall()
	return result

# 根据id获取每个商品的详细信息
def get_product_info(ids):
	for item in ids:
		url = item[2]
		# print("id:",item[0])
		try:
			if 'https:https://' in url:
				url = url[6:]
			if 'detail.tmall.com' in url:
				print("tmall:",item[0],url)
				get_product_info_and_property(item[0],item[1],url)
			elif 'item.taobao.com' in url:
				print("taobaourl:",item[0],url)
				get_product_info_from_taobao(item[0],item[1],url)
			elif 'click' in url:
				print("click:",url)
			else:
				print(item[2])
		except Exception as e:
			print(e)

'''[获取商品详情]  only for tmall
1. 从商品列表数据库依次获取每个商品数据（循环获取每个商品的详细信息）
2. 根据每个商品的详细url打开浏览器，定位每个商品参数值
3. 将解析的商品通用数据存储到商品详情表
4. 将解析的商品特有属性存储到商品属性列表
'''
def get_product_info_and_property(id,type,prodectInfoUrl):
	url = prodectInfoUrl
	if 'https' not in url:
		url = 'https:'+prodectInfoUrl
	browser.get(url)
	propertyDiv = wait.until(EC.presence_of_element_located((By.ID, "J_AttrUL")))# todo
	wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#J_DetailMeta > div.tm-clear > div.tb-property > div > ul > li.tm-ind-item.tm-ind-sellCount > div > span.tm-count')))

	productInfoHtml = browser.page_source
	productInfoDoc = pq(productInfoHtml)
	product = {
		# #J_DetailMeta > div.tm-clear > div.tb-property > div > ul > li.tm-ind-item.tm-ind-sellCount > div > span.tm-count
		'sellCount':productInfoDoc('.tm-ind-panel .tm-ind-sellCount .tm-count').text(),#月销量
		'reviewCount':productInfoDoc('.tm-ind-panel .tm-ind-reviewCount .tm-count').text(),#累计评价
		# 'reviewCount':productInfoDoc('.tm-ind-panel .tm-ind-reviewCount .tm-count').text(),#累计评价
		'emPointCount':productInfoDoc('.tm-ind-panel .tm-ind-emPointCount .tm-count').text(),#送天猫积分
		'price':productInfoDoc('#J_StrPriceModBox .tm-price').text(),#价格
		'promoPrice':productInfoDoc('#J_PromoPrice .tm-price').text(),#促销价
		'tagPrice':productInfoDoc('.tm-tagPrice-panel .tm-price').text(),#专柜价
		'coupon':productInfoDoc('.tm-coupon-panel').text()[:-4],#满减活动
		'emStock':productInfoDoc('#J_EmStock').text()[2:][:-1],#库存
		'emStockStr':productInfoDoc('#J_EmStock').text(),
		'collectCountStr':productInfoDoc('#J_CollectCount').text(),
		'collectCount':productInfoDoc('#J_CollectCount').text()[1:][:-3],# 人气
		'id':id,
		'type':type,
	}
	print(id,product['sellCount'])
	# 商品详情中通用属性保存到数据库中 pass
	save_product_info_common(product) #pass
	
	
	'''[商品属性入库]
		保存商品属性
	'''
	attributes = []
	# 1. 获取商品品牌名称J_BrandAttr > div
	# brand_name = browser.find_element_by_css_selector('#J_BrandAttr>div')
	# brandk,brandv = get_attr(brand_name.text)
	# createTime = get_current_time()
	# attributes.append((id,brandk,brandv,brandk,type,createTime))
	# 2. 获取商品的具体参数信息
	lis = browser.find_elements_by_css_selector('#J_AttrUL>li')
	for item in lis:
		itemdict = item.text
		k,v = get_attr(itemdict)
		create_Time = get_current_time()
		attributeItem = (id,k,v,k,type,create_Time)
		attributes.append(attributeItem)
		# print(attributeItem)

	attributesData = tuple(attributes)
	save_product_info_attribute(attributesData)
	print("********************************************")

# taobao 商品详情解析
def get_product_info_from_taobao(id,type,prodectInfoUrl):
	browser.get(prodectInfoUrl)
	attribute = {}
	attribute['id'] = id
	attribute['type'] = type
	# 价格 #J_DetailMeta > div.tm-clear > div.tb-property > div > div.tm-fcs-panel > dl.tm-tagPrice-panel > dd > span
	priceStr = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#J_StrPrice > em.tb-rmb-num")))
	attribute['price'] = priceStr.text
	# 淘宝价
	if isElementExist('#J_PromoPriceNum'):
		PromoPrice = wait.until(EC.presence_of_element_located((By.ID, "J_PromoPriceNum")))
		attribute['promoPrice'] = PromoPrice.text
	else:
		attribute['promoPrice'] = '0'

	# 专柜价tagPrice
	attribute['tagPrice'] = '0'
	# 累积评论
	J_RateCounter = wait.until(EC.presence_of_element_located((By.ID, "J_RateCounter")))
	attribute['reviewCount'] = J_RateCounter.text

	# 交易量
	J_SellCounter = wait.until(EC.presence_of_element_located((By.ID, "J_SellCounter")))
	attribute['sellCount'] = J_SellCounter.text
	# 库存
	J_SpanStock = wait.until(EC.presence_of_element_located((By.ID, "J_SpanStock")))
	attribute['emStock'] = J_SpanStock.text
	# 人气 #J_Social > ul > li.tb-social-fav > a > em
	renqi = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#J_Social > ul > li.tb-social-fav > a > em")))
	attribute['collectCount'] = renqi.text[1:][:-3]
	# 优惠活动 #J_OtherDiscount > div > div.tb-other-discount-content.tb-other-discount-split > div
	if isElementExist('#J_OtherDiscount > div > div.tb-other-discount-content.tb-other-discount-split > div'):
		youhui = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#J_OtherDiscount > div > div.tb-other-discount-content.tb-other-discount-split > div")))
		attribute['coupon'] = youhui.text
	else:
		attribute['coupon'] = '无'
	# 积分 #J_OtherDiscount > div > div:nth-child(1) > div > strong
	if isElementExist('#J_OtherDiscount > div > div:nth-child(1) > div > strong'):
		jifeng = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#J_OtherDiscount > div > div:nth-child(1) > div > strong")))
		attribute['emPointCount'] = jifeng.text
	else:
		attribute['emPointCount'] = '0'
	# print(id,attribute['sellCount'])
	save_product_info_common(attribute)
	
	# 淘宝商品参数（特殊）
	attributes = []
	lis = browser.find_elements_by_css_selector('#attributes .attributes-list>li')
	for item in lis:
		itemdict = item.text
		k,v = get_attr(itemdict)
		create_Time = get_current_time()
		attributeItem = (id,k,v,k,type,create_Time)
		attributes.append(attributeItem)
		# print(attributeItem)

	attributesData = tuple(attributes)
	# print(attributesData)
	save_product_info_attribute(attributesData)

def isElementExist(css):
	try:
		browser.find_element_by_css_selector(css)
		return True
	except Exception as e:
		return False
# 返回商品参数属性对 tmall
def get_attr(attrstr):
	if attrstr:
		attr_arr = attrstr.split(':')
		if len(attr_arr) < 2:
			attr_arr = attrstr.split('：')
		if len(attr_arr) > 1:
			return attr_arr[0].strip(),attr_arr[1].strip()

'''
	获取数据采集时间
'''
def get_current_time():
	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


# 保存商品通用属性 
def save_product_info_common(product):
	product_info_common_sql = 'insert into taobao_shoes_productinfo_test2(product_id,product_type,sellCount,reviewCount,emPointCount,price,promoPrice,tagPrice,coupon,emStock,collectCount) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
	cursor.execute(product_info_common_sql, (product['id'],product['type'], product['sellCount'], product['reviewCount'], product['emPointCount'], 
		product['price'],product['promoPrice'],product['tagPrice'],product['coupon'],product['emStock'],product['collectCount']))
	conn.commit()

# 保存商品特有属性 
def save_product_info_attribute(attributesData):
	product_info_attribute_sql = 'insert into taobao_product_info_property_test2(product_id,property_name,property_value,property_class,property_type,create_time) values(%s,%s,%s,%s,%s,%s)'
	cursor.executemany(product_info_attribute_sql,attributesData)
	conn.commit()

def spider(startid,endid,sorttype):
	ids = get_product_ids(startid,endid,sorttype)
	get_product_info(ids)


def close():
	browser.quit()
	cursor.close()
	conn.close()

def main():
	start = time.clock()
	spider(62217,79164,'defalt')
	end  = time.clock()
	print('running time:%s seconds' %(end-start))

# main
if __name__ == '__main__':
	main()