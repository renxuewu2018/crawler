#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: renxuewu
# @Email:  seektolive@gmail.com
# @FD:	使用selenium + phantomjs 获取微博用户
# @Date:   2018-02-09 10:39:51
# @Last Modified by:   renxuewu
# @Last Modified time: 2018-02-11 17:16:07


# 获取微博用户信息 TODO
'''
1. 获取微博用户列表
	1）从种子用户开始，打开种子用户主页
	2）获取种子用户的关注列表，需要翻页
	3）循环第二步，获取种子的所有关注用户
	4）再从获取的关注用户开始，依次作为种子用户循环获取每个用户的关注列表

2. 获取微博用户信息
	1）微博昵称，头像
	2）关注、粉丝及微博数量

判断僵尸粉（关注数数倍于粉丝数的。通过设置阈值来判断）
	僵尸粉：基本不发微博，微博数量特别少
	营销帐号：基本都是广告和转发，关注数比粉丝数多

'''
from bloom_filter import BloomFilter
from selenium import webdriver
from collections import deque
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import hashlib
from binascii import hexlify,unhexlify

import re

import threading


#  种子用户  https://m.weibo.cn/u/1192329374
seed_user_url =  'https://weibo.com/xiena'


bloom = BloomFilter(max_elements=100000, error_rate=0.1)
cur_queue = deque()

username = '' # test uname
password = '' # test pwd  error

user_agent = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4)'+
	'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36')
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap['phantomjs.page.settings.userAgent']=user_agent


feeds_crawler = webdriver.PhantomJS(desired_capabilities=dcap)
feeds_crawler.set_window_size(1920,1200)

user_crawler = webdriver.PhantomJS(desired_capabilities=dcap)
user_crawler.set_window_size(1920,1200)

# log config
import logging
import logging.config
logging.config.fileConfig('logconfig.ini')

from lxml import etree


def get_weibo_user_info():
	pass

def get_weibo_user():
	# 打开关注列表
	driver.find_element_by_xpath('//a[@class="t_link S_txt1"]').get_attribute('href')

	# 获取所关注的微博号的地址
	driver.find_element_by_xpath('//*[contain(@class,"follow_item")]//a[@class="S_txt1"]')


# 爬取的url存储到独立中
def enqueue_url(url):
	try:
		# tes = hexlify(bin(url))
		md5_value = hashlib.md5(url.encode('utf-8')).hexdigest()
		if md5_value not in bloom:
			bloom.add(md5_value)
			cur_queue.append(url)

	except Exception as e:
		raise e


'''登录
	登录手机网页版微博
'''
weibo_home_page = 'https://weibo.com/'
app_weibo_home_page = 'https://m.weibo.com'
def login(uname,pwd):

	logging.info('login....')
	feeds_crawler.get(weibo_home_page)
	user_crawler.get(weibo_home_page)

	time.sleep(8)

	logging.info('find click button to login...')
	feeds_crawler.find_element_by_id('loginname').send_keys(uname)
	wait()
	feeds_crawler.find_elements_by_name('password')[0].send_keys(pwd)
	# feeds_crawler.find_element_by_id('password').send_keys(pwd)
	wait()
	feeds_crawler.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()
	# feeds_crawler.execute_script('document.getElementByClassName("W_btn_a_32x")[0].click()')
	

	user_crawler.get(weibo_home_page)
	user_crawler.find_element_by_id('loginname').send_keys(uname)
	wait()
	user_crawler.find_elements_by_name('password')[0].send_keys(pwd)
	wait()
	user_crawler.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()


'''等待时间
	随机等待一段时间
'''
import time
import random
def wait():
	return time.sleep(random.choice(range(1,3)))

# 关闭后台浏览器（phantomjs）进程
def close():
	feeds_crawler.close()
	user_crawler.close()

# 从队列中获取元素
def dequeue_url():
	if len(cur_queue) > 0:
		return cur_queue.popleft()
	else:
		return None

# 滚动屏幕
def scroll_to_botton():
	logging.info('scroll down')
	for i in range(0,5):
		feeds_crawler.execute_script('window.scrollTo(0,document.body.scrollHeight)')
		html =  feeds_crawler.page_source
		tr = etree.HTML(html)
		next_page_url = tr.xpath('//a[contains(@class,"page next")]')
		if len(next_page_url) > 0:
			return next_page_url[0].get('href')
		if len(re.findall('点击重新载入',html)) > 0:
			logging.info('scrolling failed,reload it')
			feeds_crawler.find_element_by_link_text('点击重新载入').click()
		time.sleep(1)

# 获取用户关注列表（目前微博只能查看前5页的用户列表-20180211）
def extract_user(users):
	for i in range(0,5):
		# feeds #follow_item S_line2
		user_list = user_crawler.find_elements_by_xpath('//*[@id="Pl_Official_HisRelation__58"]/div/div/div/div[2]/div[1]/ul/li')
		print(user_list)
		for element in user_list:
			tried = 0
			while tried < 10:
				try:
					user = {}
					user['name'] = element.find_element_by_xpath('.//div[contains(@class,"info_name"]/a').text
					print(user['name'])
				except Exception as e:
					raise e


# 获取用户信息
def get_user(user_link):
	logging.info('downloading:'+user_link)
	feeds_crawler.get(user_link)
	wait()

	# 提取用户名
	account_name = get_element_by_xpath(feeds_crawler,'//h1')[0].text

	# 提取用户头像图片
	photo = get_element_by_xpath(feeds_crawler,'//p[@class="photo_wrap"]/img')[0].get('src')
	account_photo = re.findall('/([^/]+)$',photo)

	# 提取关注列表url
	watch_list_link = get_element_by_xpath(feeds_crawler,'//a[@class="t_link S_txt1"]')[0].get('href')

	logging.info('account_name'+account_name)
	logging.info('wait_list_link'+watch_list_link)

	print(account_name,watch_list_link)

	user_crawler.get(watch_list_link)

	feeds = []
	users = []

	# t_feeds = threading.Thread(target=get_watch,name=None,args=(feeds,))
	# t_feeds.setDaemon(True)
	# t_feeds.start()
	# t_feeds.join()

	t_users = threading.Thread(target=extract_user, name=None, args=(users,))
	t_users.setDaemon(True)
	t_users.start()
	t_users.join()

# 根据xpath路径获取元素
def get_element_by_xpath(cur_driver,path):
	tried = 0
	while tried < 6:
		html = cur_driver.page_source
		tr = etree.HTML(html)
		element = tr.xpath(path)
		if len(element) == 0:
			wait()
			continue
		return element
	pass

# 爬取数据
def crawler():
	while True:
		url = dequeue_url()
		if url == None:
			continue
		get_user(url)

def main():
	enqueue_url(seed_user_url)
	login(username,password)
	crawler()
	close()

if __name__ == '__main__':
	main()