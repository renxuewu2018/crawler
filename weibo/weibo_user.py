#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: renxuewu
# @Email:  seektolive@gmail.com
# @FD:	使用selenium + phantomjs 获取微博用户
# @Date:   2018-02-09 10:39:51
# @Last Modified by:   renxuewu
# @Last Modified time: 2018-02-09 17:11:57



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


#  种子用户
seed_user_url =  'https://weibo.com/xiena'

bloom = BloomFilter(max_elements=100000, error_rate=0.1)
cur_queue = deque()

username = '18600663368'
password = 'B69-FNw-Crq-BmT'

feeds_crawler = webdriver.PhantomJS(desired_capabilities=dcap)

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
		md5_value = hashlib.md5(url).hexdigest()
		if md5_value not in bloom:
			bloom.add(md5_value)
			cur_queue.append(url)

	except Exception as e:
		raise e

def login(uname,pwd):
	

def main():
	enqueue_url()
	login()

if __name__ == '__main__':
	main()