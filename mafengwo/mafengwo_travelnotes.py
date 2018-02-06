#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: xwren
# @Email:  seektolive@gmail.com
# @FD:	马蜂窝游记爬取练习
# @Date:   2018-02-06 09:58:06
# @Last Modified by:   xwren
# @Last Modified time: 2018-02-06 14:46:55

''' 网站结构分析
1、网站所有的游记都位于WWW.mafengwo.cn/mdd下，并且是按城市分类的。
	WWW.mafengwo.cn/mdd 网站所有目的地
2、城市的页面：如下，后面的数字代表不太同的省份和城市
	http://www.mafengwo.cn/travel-scenic-spot/mafengwo/13033.html 山西
	http://www.mafengwo.cn/travel-scenic-spot/mafengwo/10440.html 黄山

	下面信息可以查找景点信息
	http://www.mafengwo.cn/mdd/map/13033.html 山西所有目的地
	http://www.mafengwo.cn/mdd/base/map/getCityList 目的地列表

	http://www.mafengwo.cn/poi/5429065.html 具体目的地信息概括
3、游记图片
	http://www.mafengwo.cn/photo/mdd/13033.html 整体
	http://www.mafengwo.cn/photo/mdd/13033_32244561.html 单张图片	
4、游记列表数据
	http://www.mafengwo.cn/yj/13033/1-0-1.html	第一页 
	http://www.mafengwo.cn/yj/13033/1-0-200.html	最后一页
	http://www.mafengwo.cn/yj/13033/1-0-2000.html 该筛选条件下暂时没有数据
5、游记具体信息（在列表中有具体游记的超链接）
	http://www.mafengwo.cn/i/3540745.html
'''
import requests
import re

home_page = 'http://www.mafengwo.cn'

mmd_url_req_headers = {
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'Accept-Encoding': "gzip, deflate",
    'Accept-Language': "zh-CN,zh;q=0.9",
    'Cache-Control': "no-cache",
    'Cookie': "mfw_uuid=5a6969b2-cf72-76b6-362a-68f4231a32d1; _r=google; _rp=a%3A2%3A%7Bs%3A1%3A%22p%22%3Bs%3A15%3A%22www.google.com%2F%22%3Bs%3A1%3A%22t%22%3Bi%3A1516857778%3B%7D; uva=s%3A150%3A%22a%3A4%3A%7Bs%3A13%3A%22host_pre_time%22%3Bs%3A10%3A%222018-01-25%22%3Bs%3A2%3A%22lt%22%3Bi%3A1516857780%3Bs%3A10%3A%22last_refer%22%3Bs%3A23%3A%22https%3A%2F%2Fwww.google.com%2F%22%3Bs%3A5%3A%22rhost%22%3Bs%3A14%3A%22www.google.com%22%3B%7D%22%3B; __mfwurd=a%3A3%3A%7Bs%3A6%3A%22f_time%22%3Bi%3A1516857780%3Bs%3A9%3A%22f_rdomain%22%3Bs%3A14%3A%22www.google.com%22%3Bs%3A6%3A%22f_host%22%3Bs%3A3%3A%22www%22%3B%7D; __mfwuuid=5a6969b2-cf72-76b6-362a-68f4231a32d1; UM_distinctid=1612bc4e86c350-03f4f525e1d7c4-5e183017-15f900-1612bc4e86d9f6; PHPSESSID=6avom5l4j90t7q9cft2i034lu4; oad_n=a%3A5%3A%7Bs%3A5%3A%22refer%22%3Bs%3A22%3A%22https%3A%2F%2Fwww.google.com%22%3Bs%3A2%3A%22hp%22%3Bs%3A14%3A%22www.google.com%22%3Bs%3A3%3A%22oid%22%3Bi%3A1075%3Bs%3A2%3A%22dm%22%3Bs%3A15%3A%22www.mafengwo.cn%22%3Bs%3A2%3A%22ft%22%3Bs%3A19%3A%222018-02-06+09%3A46%3A29%22%3B%7D; __mfwlv=1517881678; __mfwvn=2; CNZZDATA30065558=cnzz_eid%3D5734503-1516857710-https%253A%252F%252Fwww.google.com%252F%26ntime%3D1517885366; __mfwlt=1517888787",
    'Host': "www.mafengwo.cn",
    'Proxy-Connection': "keep-alive",
    'Upgrade-Insecure-Requests': "1",
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36",
    }

travelnote_root = 'mafengwo_travelnote_page/'
# 保存游记
def save_travelnote_page(filename,page):
	print('start crawler %s page...' %(filename))
	with open('%s%s.html' %(travelnote_root,filename), 'wb+') as f:
		f.write(page)

url_ids = []
# 下载游记
def download_travelnote_page(url_id):
	for page_num in range(1,2):
		city_travelnote_url = 'http://www.mafengwo.cn/yj/%s/1-0-%d.html' %(url_id,page_num)
		if url_id in url_ids:
			continue
		url_ids.append(city_travelnote_url)
		travelnote_page = requests.get(city_travelnote_url,headers = mmd_url_req_headers).text
		city_travelnote_urls = re.findall('href="/i/\d{7}.html', travelnote_page)

		if len(city_travelnote_urls) == 0:
			return 
		for item in city_travelnote_urls:
			try:
				city_travelnote_url = home_page + item[6:]
				city_travelnote_page = requests.get(city_travelnote_url,headers=mmd_url_req_headers).content
				save_travelnote_page(url_id,city_travelnote_page)
			except Exception as e:
				raise e
			else:
				pass
# 查找游记页面
def crawler():
	try:
		# 1、下载目的地首页
		mdd_url = 'http://www.mafengwo.cn/mdd/'
		mdd_page = requests.get(mdd_url,headers=mmd_url_req_headers).text

		# 利用正则表达式，找出所有的城市主页
		city_urls = re.findall('/travel-scenic-spot/mafengwo/\d{5}.html', mdd_page)

		# 2、循环依次下载每个城市的所有游记
		for item in city_urls:
			download_travelnote_page(item[29:34])

	except Exception as e:
		raise e
	else:
		pass

def main():
	crawler()

if __name__ == '__main__':
	main()
