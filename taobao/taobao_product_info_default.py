# -*- coding: utf-8 -*-
# @Author: xwren
# 根据商品ID获取商品详细信息
# @Date:   2017-12-19 14:15:29
# @Last Modified by:   renxuewu
# @Last Modified time: 2018-04-17 09:39:39
# @version 1.0
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

'''
	打开浏览器
'''
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 5)
browser.maximize_window()
queryKeyword = u'领带'
'''
	1. 根据关键字获取商品列表内的信息
'''
def get_product_list(orderby):
	# total = spider_by_keyword(queryKeyword)   renqi  price-asc
	total = spider_by_keyword_and_sort(queryKeyword,orderby)
	total = int(re.compile('(\d+)').search(total).group(1))
	for i in range(2,total):
		time.sleep(random.choice(range(2,5)))
		print('====================')
		next_page(i,orderby)


'''
	根据关键字查询商品信息（默认排序）
	1、进入淘宝网
	2、输入查询关键字
	3、按列表方式展示
	3、处理当前页面的产品信息
	4、跳转到下一页面
'''
# #J_relative > div.sort-row > div > ul > li:nth-child(2) > a
def spider_by_keyword(queryKeyword):
	try:
		browser.get('https://www.taobao.com/')
		input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#q")))
		submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_TSearchForm > div.search-button > button')))
		input.send_keys(queryKeyword)
		submit.click()
		time.sleep(1)
		# //*[@id="J_relative"]/div[1]/div/div[3]/ul/li[2]/a/span
		link = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="J_relative"]/div[1]/div/div[3]/ul/li[2]/a/span')))
		link.click()
		time.sleep(2)
		# #mainsrp-pager > div > div > div > div.total
		# #mainsrp-pager > div > div > div > div.total
		total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.total')))
		get_products()

		print(total.text)
		return total.text
	except TimeoutException:
		return spider_by_keyword(queryKeyword)

'''
根据关键字查询商品信息（根据不同的排序字段进行）
'''
def spider_by_keyword_and_sort(queryKeyword,sort):
	try:
		browser.get('https://www.taobao.com/')
		input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#q")))
		submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_TSearchForm > div.search-button > button')))
		input.send_keys(queryKeyword)
		submit.click()
		time.sleep(1)
		if sort == 'renqi':
			# 人气排序 //*[@id="J_relative"]/div[1]/div/ul/li[2]/a
			renqi_desc_link = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="J_relative"]/div[1]/div/ul/li[2]/a')))
			renqi_desc_link.click()
			time.sleep(3)
		elif sort == 'sale':
			# 销量排序 //*[@id="J_relative"]/div[1]/div/ul/li[3]/a
			sale_desc_link = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="J_relative"]/div[1]/div/ul/li[3]/a')))
			sale_desc_link.click()
			time.sleep(3)
		elif sort == 'price-asc':
			# //*[@id="J_relative"]/div[1]/div/ul/li[5]/ul/li[1]/a   价格从高到低   price-desc
			# //*[@id="J_relative"]/div[1]/div/ul/li[5]/ul/li[2]/a   价格从低到高   price-asc
			# //*[@id="J_relative"]/div[1]/div/ul/li[5]/ul/li[3]/a   总价从低到高	total-asc
			# //*[@id="J_relative"]/div[1]/div/ul/li[5]/ul/li[4]/a   总价从高到低	taotal-desc
			price= wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="J_relative"]/div[1]/div/ul/li[5]/div/div/span[1]')))
			ActionChains(browser).move_to_element(price).perform()
			time.sleep(1)

			price_asc_link = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="J_relative"]/div[1]/div/ul/li[5]/ul/li[2]/a')))
			price_asc_link.click()
			time.sleep(3)

		elif sort == 'price-desc':
			price= wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="J_relative"]/div[1]/div/ul/li[5]/div/div/span[1]')))
			ActionChains(browser).move_to_element(price).perform()
			time.sleep(1)

			price_desc_link = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="J_relative"]/div[1]/div/ul/li[5]/ul/li[1]/a')))
			price_desc_link.click()
			time.sleep(3)

		elif sort == 'total-asc':
			price= wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="J_relative"]/div[1]/div/ul/li[5]/div/div/span[1]')))
			ActionChains(browser).move_to_element(price).perform()
			time.sleep(1)

			total_asc_link = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="J_relative"]/div[1]/div/ul/li[5]/ul/li[3]/a')))
			total_asc_link.click()
			time.sleep(3)
		elif sort == 'total-desc':
			price= wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="J_relative"]/div[1]/div/ul/li[5]/div/div/span[1]')))
			ActionChains(browser).move_to_element(price).perform()
			time.sleep(1)

			total_desc_link = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="J_relative"]/div[1]/div/ul/li[5]/ul/li[4]/a')))
			total_desc_link.click()
			time.sleep(3)
		else:
			print('defalt')
			time.sleep(5)

		link = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="J_relative"]/div[1]/div/div[3]/ul/li[2]/a/span')))
		link.click()
		time.sleep(2)
		# 获取页面总数
		total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.total')))
		
		# 解析获取商品信息
		get_products(sort)

		print(total.text)
		return total.text
	except TimeoutException:
		return spider_by_keyword_and_sort(queryKeyword,sort)
'''
	采集下一页的产品数据
	1、跳转下一页
	2、采集当前页面的产品信息
'''
def next_page(page_number,orderby):
	try:
		input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input")))
		submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
		input.clear()
		input.send_keys(page_number)
		submit.click()
		wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > ul > li.item.active > span'),str(page_number)))
		get_products(orderby)
	except TimeoutException:
		next_page(page_number,orderby)

'''
	循环获取当前页面列表中商品信息
'''
def get_products(orderby):
	wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-itemlist .items .item')))
	html = browser.page_source
	doc = pq(html)
	items = doc('#mainsrp-itemlist .items .item').items()
	products = []
	for item in items:
		product = {
			'image':item.find('.pic .img').attr('src'),
			'price':item.find('.price').text()[2:],
			'deal':item.find('.deal-cnt').text()[:-5],
			'title':item.find('.title').text(),
			'shop':item.find('.shop').text(),
			'location':item.find('.location').text(),
			'detailedInfoUrl':item.find('.J_ClickStat').attr('href'),
			'discussNum':item.find('.comment').text()[:-3],
		}
		print(product)
		detailedInfoUrl = 'https:' + product['detailedInfoUrl']
		product['detailedInfoUrl'] = detailedInfoUrl
		print('---------------------------------------')

		'''
			获取详情页面 待完成
		'''
		# if 'click' not in detailedInfoUrl:
		#     get_product_info(detailedInfoUrl)
		
		imageUrl = 'https:' + product['image']
		product['imageUrl'] = imageUrl
		insertTime = get_current_time()
		product['insertTime'] = insertTime
		product['queryKeyword'] = queryKeyword
		product['orderby'] = orderby
		save_list_data_by_only(product)
		# 或采用批量导入的方法
		# products.append((product))
	# 批量导入的方式
	# save_list_data_by_many(products)


'''
	连接数据库
'''
conn = mysql.connector.connect(
	user='root', password='imsbase', database='spider')
cursor = conn.cursor()
# cursor = conn.cursor(cursorclass=mysql.cursors.DictCursor)

# 将商品列表信息存储到数据库中
sql = 'insert into taobao_productlist(title,price,salesNum,merchant,location,discussNum,detailedInfoUrl,imageUrl,queryKeyword,createTime)  values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
# 无良印品
muji_sql = 'insert into taobao_productlist_muji(title,price,salesNum,merchant,location,discussNum,detailedInfoUrl,imageUrl,queryKeyword,createTime,orderby)  values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

'''
	将列表中商品信息存储到数据库中（一条一条入库）
'''
def save_list_data_by_only(product):
	cursor.execute(muji_sql, (product['title'],product['price'], product['deal'], product['shop'], product['location'], 
		product['discussNum'],product['detailedInfoUrl'],product['imageUrl'],product['queryKeyword'],product['insertTime'],product['orderby']))
	conn.commit()
'''
	将列表中商品信息存储到数据库中（批量插入）
'''
many_sql = 'insert into taobao_productlist(title,price,salesNum,merchant,location,discussNum,detailedInfoUrl,imageUrl,queryKeyword,createTime)  values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
def save_list_data_by_many(products):
	cursor.executemany(sql,products.values)
	conn.commit()


'''
	获取数据采集时间
'''
def get_current_time():
	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


'''
	功能：获取淘宝商品详细信息
'''
def get_product_info_from_tmall(prodectInfoUrl):
	browser.get(prodectInfoUrl)
	time.sleep(1)
	#J_PromoPrice > dd > div > span
	wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#J_PromoPrice > dd > div > span')))

	'''[summary]
	   only  tmall
	[description]
	'''
	productInfoHtml = browser.page_source
	productInfoDoc = pq(productInfoHtml)
	product = {
		'sellCount':productInfoDoc('.tm-ind-panel .tm-ind-sellCount .tm-count').text(),#月销量
		'reviewCount':productInfoDoc('.tm-ind-panel .tm-ind-reviewCount .tm-count').text(),#累计评价
		'reviewCount':productInfoDoc('.tm-ind-panel .tm-ind-reviewCount .tm-count').text(),#累计评价
		'emPointCount':productInfoDoc('.tm-ind-panel .tm-ind-emPointCount .tm-count').text(),#送天猫积分
		'price':productInfoDoc('#J_StrPriceModBox .tm-price').text(),#价格
		'promoPrice':productInfoDoc('#J_PromoPrice .tm-price').text(),#促销价
		'tagPrice':productInfoDoc('.tm-tagPrice-panel .tm-price').text(),#专柜价
		'coupon':productInfoDoc('.tm-coupon-panel').text(),#满减活动
		'emStock':productInfoDoc('#J_EmStock').text(),#库存
	}
	print(product)
	# attr 商品属性  $('#J_AttrUL')
	# 以下代码需要修改
	test1 = productInfoDoc('#J_AttrUL').items()
	print(test1)
	for item in test1:
		print(item.text())
	'''[summary]
		only taobao
	'''
	brand_name = browser.find_element_by_css_selector('#J_BrandAttr > div')
	print(brand_name.text)
	print("********************************************")
	k,v = get_attr(brand_name.text)
	print(k,':',v)
	lis = browser.find_elements_by_css_selector('#J_AttrUL>li')
	for item in lis:
		itemdict = item.text
		k,v = get_attr(itemdict)
		print(k,':',v)
		# print(itemdict)
		# print('+++++++++++++++++++++++')
		# item_str =  itemdict.split(':')
		# if len(item_str) < 2:
		# 	item_str = itemdict.split('：')
		# print(len(item_str))
		# if len(item_str) > 1:
		# 	print('name:',item_str[0].strip())
		# 	print('value:',item_str[1].strip())

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
	print(id,attribute['sellCount'])
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

def is_element_exist(css):
	e = browser.find_element_by_css_selector(css_selector=css)
	if len(e) == 0:
		print('不存在在元素')
		return False
	elif len(e) == 1:
		return True
	else:
		print('找到多个元素')
		return False


'''
	获取商品评论信息（目前只获取第一页信息）
'''
def get_comment(url):
	# tm-rate-content $('.rate-grid tr')
	browser.get(url)
	time.sleep(2)
	productInfoHtml = browser.page_source
	productInfoDoc = pq(productInfoHtml)
	items = productInfoDoc('.rate-grid tr').items()
	comments = []
	for item in items:
		commont = {
			'commont_time':item.find('.tm-rate-date').text(),
			'commont_dis':item.find('.tm-rate-content .tm-rate-fulltxt').text(),
			'commont_reply':item.find('.tm-rate-reply .tm-rate-fulltxt').text(),
			'commont_author':item.find('.col-author .rate-user-info').text(),
			'commont_author_grade':item.find('.gold-user').text(),
			# 'commont_time':item.find('.tm-rate-date').text(),
		}
		print(commont)
		comments.append(commont)
	import pandas
	df = pandas.DataFrame(comments)
	df.to_excel('comments.xlsx',encoding='utf-8')

# 关闭数据库
def close_db():
	sava_error_ids()
	cursor.close()
	conn.close()
	browser.close()

'''[获取无良印品商品详情]
1. 从商品列表数据库依次获取每个商品数据（循环获取每个商品的信息信息）
2. 根据每个商品的详细url打开浏览器，定位每个商品参数值
3. 将解析的商品通用数据存储到商品详情表
4. 将解析的商品特有属性存储到商品属性列表
'''
def get_muji_shoes_product_info(url):
	url = 'https:'+url
	get_product_info_from_tmall(url)
	# browser.get(url)
# 从数据库获取无良印品产品的url pass
def get_muji_shoes_product_url():
	muji_shoes_sql = 'select * from taobao_shop_muji_shoes_productlist'
	cursor.execute(muji_shoes_sql)
	shoes_list = cursor.fetchall()
	for shoe_item in shoes_list:
		# get_muji_shoes_product_info(shoe_item[3])
		get_product_info_and_property(shoe_item[0],'MUJI 鞋',shoe_item[3])

# 根据id获取此id之后所有id编码，然后在根据id获取商品信息 67000
def get_shoes_product_url(id=62225):
	shoes_sql = 'select t.id,t.queryKeyword,t.detailedInfoUrl from taobao_productlist t where  t.id >'+str(id)
	cursor.execute(shoes_sql)
	shoes_list = cursor.fetchall()
	for shoe_item in shoes_list:
		url = shoe_item[2]
		print("id:",shoe_item[0])
		try:
			if 'https:https://' in url:
				url = url[6:]
			if 'detail.tmall.com' in url:
				get_product_info_and_property(shoe_item[0],shoe_item[1],url)
			elif 'item.taobao.com' in url:
				get_product_info_from_taobao(shoe_item[0],shoe_item[1],url)
			elif 'click' in url:
				# get_product_info_and_property(shoe_item[0],shoe_item[1],url)
				print(url)
			else:
				print(shoe_item[2])
				comments.append(shoe_item[0])
		except Exception as e:
			# raise e
			# print(e)
			comments.append(shoe_item[0])
			get_shoes_product_url(shoe_item[0])

import pandas
comments = []

def sava_error_ids():
	df = pandas.DataFrame(comments)
	df.to_csv('ids.cvs')


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
# 保存商品详细参数
def save_product_info_attribute(attributesData):
	product_info_attribute_sql = 'insert into taobao_product_info_property_test2(product_id,property_name,property_value,property_class,property_type,create_time) values(%s,%s,%s,%s,%s,%s)'
	cursor.executemany(product_info_attribute_sql,attributesData)
	conn.commit()

# 返回商品参数属性对 tmall
def get_attr(attrstr):
	if attrstr:
		attr_arr = attrstr.split(':')
		if len(attr_arr) < 2:
			attr_arr = attrstr.split('：')
		if len(attr_arr) > 1:
			return attr_arr[0].strip(),attr_arr[1].strip()

# sql = 'insert into taobao_productlist(title,price,salesNum,merchant,location,discussNum,detailedInfoUrl,imageUrl,queryKeyword,createTime) 
# values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
def save_product_info_common(product):
	product_info_common_sql = 'insert into taobao_shoes_productinfo_test2(product_id,product_type,sellCount,reviewCount,emPointCount,price,promoPrice,tagPrice,coupon,emStock,collectCount) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
	cursor.execute(product_info_common_sql, (product['id'],product['type'], product['sellCount'], product['reviewCount'], product['emPointCount'], 
		product['price'],product['promoPrice'],product['tagPrice'],product['coupon'],product['emStock'],product['collectCount']))
	conn.commit()
'''获取无良印品产品列表（表：taobao_shop_muji_shoes_productlist）  手工录入，暂时没有写程序
功能：
	根据店铺链接，获取店铺下的产品列表，并存储到数据库中
属性定位：
	1. 价格//*[@id="J_ShopSearchResult"]/div/div[3]/div[1]/dl[1]/dd[2]/div/div[1]/span[2]
	#J_ShopSearchResult > div > div.J_TItems > div:nth-child(1) > dl:nth-child(1) > dd.detail > div > div.cprice-area > span.c-price
	2. 标题：//*[@id="J_ShopSearchResult"]/div/div[3]/div[1]/dl[1]/dd[2]/a
	#J_ShopSearchResult > div > div.J_TItems > div:nth-child(1) > dl:nth-child(1) > dd.detail > a
	
	//*[@id="J_ShopSearchResult"]/div/div[3]
	#J_ShopSearchResult > div > div.J_TItems

	//*[@id="J_ShopSearchResult"]/div/div[3]/div[1]
	#J_ShopSearchResult > div > div.J_TItems > div:nth-child(1)

'''
def get_muji_shoes_product_list():
	shoes_url = 'https://muji.tmall.com/category-910230165-941968948.htm?spm=a1z10.5-b.w5003-7056562609.15.vSnOeg&search=y&catName=%D0%AC&scene=taobao_shop#bd'
	pass

#  程序运行
def main():
	start = time.clock()
	get_shoes_product_url()
	close_db()
	end = time.clock()
	print('running time:%s seconds' %(end-start))

if __name__ == '__main__':
	main()

	
