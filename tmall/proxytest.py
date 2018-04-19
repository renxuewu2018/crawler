#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: renxuewu
# @Email:  seektolive@gmail.com
# @Date:   2018-04-17 10:47:52
# @Last Modified by:   renxuewu
# @Last Modified time: 2018-04-19 15:00:49
from selenium import webdriver

def test_chrom():
	chromeOptions = webdriver.ChromeOptions()

	# 设置代理
	chromeOptions.add_argument("--proxy-server=http://50.233.137.38:80")
	# 一定要注意，=两边不能有空格，不能是这样--proxy-server = http://202.20.16.82:10152
	browser = webdriver.Chrome(chrome_options = chromeOptions)

	
	browser.get("http://httpbin.org/ip")
	print(browser.page_source)

	# 退出，清除浏览器缓存
	browser.quit()



import requests   

if __name__ == '__main__':
	proxies = { "http": "http://121.121.125.55:80"}  
	# proxies = {"http":''} 
	res = requests.get("http://httpbin.org/ip", proxies=proxies).text
	print(res)