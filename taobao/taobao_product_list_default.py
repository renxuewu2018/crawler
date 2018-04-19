# -*- coding: utf-8 -*-
# @Author: xwren
#  根据关键字获取商品信息（包括排序） 
# @Date:   2017-12-19 14:15:29
# @Last Modified by:   renxuewu
# @Last Modified time: 2018-04-16 14:41:34
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

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)
browser = webdriver.Chrome(chrome_options=chrome_options)
wait = WebDriverWait(browser, 5)
browser.maximize_window()

# 关键字设置
queryKeyword = u'领带'
website = 'https://www.taobao.com/'
'''
	1. 根据关键字获取商品列表内的信息
'''
def get_product_list(orderby):
	total = spider_by_keyword_and_sort(queryKeyword,orderby)
	total = int(re.compile('(\d+)').search(total).group(1))
	for i in range(2,total):
		time.sleep(random.choice(range(2,5)))# 随机停止2-5秒，避免爬取太快，淘宝屏蔽
		print('====================')
		next_page(i,orderby)

'''
   2. 根据关键字和排序条件查询商品信息（根据不同的排序字段进行）
'''
def spider_by_keyword_and_sort(queryKeyword,sort):
	try:
		browser.get(website)
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
  4. 采集下一页的产品数据
	1）跳转下一页
	2）采集当前页面的产品信息
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
	3. 循环获取当前页面列表中商品信息
'''
def get_products(orderby):
	wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-itemlist .items .item')))
	html = browser.page_source
	doc = pq(html)
	items = doc('#mainsrp-itemlist .items .item').items()
	products = []
	for item in items:
		product = {
			'price':item.find('.price').text()[2:],
			'deal':item.find('.deal-cnt').text()[:-5],
			'title':item.find('.title').text(),
			'shop':item.find('.shop').text(),
			'location':item.find('.location').text(),
			'detailedInfoUrl':item.find('.J_ClickStat').attr('href'),
			'discussNum':item.find('.comment').text()[:-3],
		}
		# print(product)
		detailedInfoUrl = 'https:' + product['detailedInfoUrl']
		product['detailedInfoUrl'] = detailedInfoUrl
		print('---------------------------------------')

		
		# imageUrl = 'https:' + product['image']
		# product['imageUrl'] = imageUrl
		insertTime = get_current_time()
		product['insertTime'] = insertTime
		product['queryKeyword'] = queryKeyword
		product['orderby'] = orderby
		print(product)
		save_list_data_by_only(product)
		# 或采用批量导入的方法
		# products.append((product))
	# 批量导入的方式
	# save_list_data_by_many(products)

'''
	连接数据库
'''
conn = mysql.connector.connect(
	user='root', password='imsbase', database='taobao')
cursor = conn.cursor()
# cursor = conn.cursor(cursorclass=mysql.cursors.DictCursor)

# 将商品列表信息存储到数据库中
sql = 'insert into tie_productlist_default(title,price,salesNum,merchant,location,discussNum,detailedInfoUrl,queryKeyword,createTime,orderby)  values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
'''
	将列表中商品信息存储到数据库中（一条一条入库）
'''
def save_list_data_by_only(product):
	cursor.execute(sql, (product['title'],product['price'], product['deal'], product['shop'], product['location'], 
		product['discussNum'],product['detailedInfoUrl'],product['queryKeyword'],product['insertTime'],product['orderby']))
	conn.commit()

'''
	根据关键字查询商品信息（默认排序）
	1、进入淘宝网
	2、输入查询关键字
	3、按列表方式展示
	3、处理当前页面的产品信息
	4、跳转到下一页面
'''
def spider_by_keyword(queryKeyword):
	try:
		browser.get('https://www.taobao.com/')
		input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="q"]')))
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


# 关闭数据库
def close_db():
	# sava_error_ids()
	cursor.close()
	conn.close()
	browser.close()

#  程序运行
def main():
	start = time.clock()
	# spider_by_keyword(queryKeyword)
	#根据关键字和查询条件获取商品列表信息(pass)  price-desc
	orderbylist = ['defalt']
	# orderbylist = ['defalt','renqi','sale','price-asc','price-desc','total-asc','total-desc']
	for orderby in orderbylist:
		get_product_list(orderby)
	close_db()
	end = time.clock()
	print('running time:%s seconds' %(end-start))

if __name__ == '__main__':
	main()

	
