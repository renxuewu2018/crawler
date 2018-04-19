import re
from collections import OrderedDict
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq   #获取整个网页的源代码
from config import *   #可引用congif的所有变量

import pymysql
import urllib
import json
import bs4
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from pyquery import PyQuery as pq   #获取整个网页的源代码
import pandas as pd

#  测试  淘宝+天猫，可完整输出及保存


browser = webdriver.Chrome()
wait = WebDriverWait(browser,10)

#######  天猫上半部分详情 #############
def get_tianmao_header(url):
    browser.get(url)
    # wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'#mainsrp-itemlist .items .item'))) #加载所有宝贝
    html=browser.page_source
    doc = pq(html)
    # print(doc)
    info = OrderedDict()  # 存放该商品所具有的全部信息
    items = doc('#page')

    # info['店铺名'] = items.find('.slogo').find('.slogo-shopname').text()
    # info['ID'] = items.find('#LineZing').attr['itemid']
    info['宝贝'] = items.find('.tb-detail-hd').find('h1').text()
    info['促销价'] = items.find('#J_PromoPrice').find('.tm-promo-price').find('.tm-price').text()
    info['原价'] = items.find('#J_StrPriceModBox').find('.tm-price').text()
    # '月销量' :items.find('.tm-ind-panel').find('.tm-ind-item tm-ind-sellCount').find('.tm-indcon').find('.tm-count').text(),
    info['月销量'] = items.find('.tm-ind-panel').find('.tm-indcon').find('.tm-count').text().split(' ',2)[0]
    info['累计评价'] = items.find('#J_ItemRates').find('.tm-indcon').find('.tm-count').text()
    # print(info)
    return info

######## 淘宝上半部分详情 ###############
def get_taobao_header(url):
    browser.get(url)
    # wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'#mainsrp-itemlist .items .item'))) #加载所有宝贝
    html=browser.page_source
    doc = pq(html)
    # print(doc)
    info = OrderedDict()  # 存放该商品所具有的全部信息
    items = doc('#page')

    # info['店铺名'] = items.find('.tb-shop-seller').find('.tb-seller-name').text()
    # info['ID'] = items.find('#J_Pine').attr['data-itemid']
    info['宝贝'] = items.find('#J_Title').find('h3').text()
    info['原价'] = items.find('#J_StrPrice').find('.tb-rmb-num').text()
    info['促销价'] = items.find('#J_PromoPriceNum').text()
    # '月销量' :items.find('.tm-ind-panel').find('.tm-ind-item tm-ind-sellCount').find('.tm-indcon').find('.tm-count').text(),
    info['月销量'] = items.find('#J_SellCounter').text()
    info['累计评价'] = items.find('#J_RateCounter').text()
    # print(info)
    return info



#######################  详情  ############################
# 抓取所有商品详情
def get_Details(attrs,info):
    # res = requests.get(url)
    # soup = BeautifulSoup(res.text, "html.parser")
    #
    # attrs = soup.select('.attributes-list li')

    #  attrs= [<li title=" 薄">厚薄: 薄</li>, <li title=" 其他100%">材质成分: 其他100%</li>,<li ...</li>]
    attrs_name = []
    attrs_value = []
    '''
    [\s] 匹配空格，[\s]*,后面有 *，则可以为空
    * : 匹配前面的子表达式任意次
    '''

    for attr in attrs:
        attrs_name.append(re.search(r'(.*?):[\s]*(.*)', attr.text).group(1))
        attrs_value.append(re.search(r'(.*?):[\s]*(.*)', attr.text).group(2))

    # print('attrs_name=',attrs_name)   # attrs_name= ['厚薄', '材质成分', ...]
    # print('attrs_value=',attrs_value)   # attrs_value= ['薄', '其他100%', ...]

    allattrs = OrderedDict()  # 存放该产品详情页面所具有的属性
    for k in range(0, len(attrs_name)):
        allattrs[attrs_name[k]] = attrs_value[k]
    # print('allattrs=',allattrs)   #  allattrs= OrderedDict([('厚薄', '薄'), ('材质成分', '其他100%'),...])

    # info = OrderedDict()  # 存放该商品所具有的全部信息
    # info = get_headdetail2(url)

    # 下面三条语句获取描述、服务、物流的评分信息

    # 下面的语句用来判断该商品具有哪些属性，如果具有该属性，将属性值插入有序字典，否则，该属性值为空
    # 适用场景
    if '材质成分' in attrs_name:
        info['材质成分'] = allattrs['材质成分']
    elif '面料' in attrs_name:
        info['材质成分'] = allattrs['面料']
    else:
        info['材质成分'] = 'NA'

    # 适用对象
    if '流行元素' in attrs_name:
        info['流行元素'] = allattrs['流行元素']
    else:
        info['流行元素'] = 'NA'

    #季节
    if '年份季节' in attrs_name:
        info['年份季节'] = allattrs['年份季节']
    else:
        info['年份季节'] = 'NA'

    # 款式
    if '袖长' in attrs_name:
        info['袖长'] = allattrs['袖长']
    else:
        info['袖长'] = 'NA'
    # 尺码
    if '销售渠道类型' in attrs_name:
        info['销售渠道类型'] = allattrs['销售渠道类型']
    else:
        info['销售渠道类型'] = 'NA'
    # 帽顶款式
    if '货号' in attrs_name:
        info['货号'] = allattrs['货号']
    else:
        info['货号'] = 'NA'
    # 帽檐款式
    if '服装版型' in attrs_name:
        info['服装版型'] = allattrs['服装版型']
    else:
        info['服装版型'] = 'NA'
    # 檐形
    if '衣长' in attrs_name:
        info['衣长'] = allattrs['衣长']
    else:
        info['衣长'] = 'NA'
    # 主要材质
    if '领型' in attrs_name:
        info['领型'] = allattrs['领型']
    else:
        info['领型'] = 'NA'
    # 人群
    if '袖型' in attrs_name:
        info['袖型'] = allattrs['袖型']
    else:
        info['袖型'] = 'NA'
    # 品牌
    if '品牌' in attrs_name:
        info['品牌'] = allattrs['品牌']
    else:
        info['品牌'] = 'NA'
    # 风格
    if '图案' in attrs_name:
        info['图案'] = allattrs['图案']
    elif  '中老年女装图案' in attrs_name:
        info['图案'] = allattrs['中老年女装图案']
    else:
        info['图案'] = 'NA'

    # 款式细节
    if '服装款式细节' in attrs_name:
        info['服装款式细节'] = allattrs['服装款式细节']
    else:
        info['服装款式细节'] = 'NA'

    # 适用年龄
    if '适用年龄' in attrs_name:
        info['适用年龄'] = allattrs['适用年龄']
    else:
        info['适用年龄'] = 'NA'

    # 风格
    if '风格' in attrs_name:
        info['风格'] = allattrs['风格']
    elif '中老年风格' in attrs_name:
        info['风格'] = allattrs['中老年风格']
    else:
        info['风格'] = 'NA'

    #通勤
    if '通勤' in attrs_name:
        info['通勤'] = allattrs['通勤']
    else:
        info['通勤'] = 'NA'

    if '裙长' in attrs_name:
        info['裙长'] = allattrs['裙长']
    else:
        info['裙长'] = 'NA'

    if '裙型' in attrs_name:
        info['裙型'] = allattrs['裙型']
    else:
        info['裙型'] = 'NA'

    if '腰型' in attrs_name:
        info['腰型'] = allattrs['腰型']
    else:
        info['腰型'] = 'NA'

    # 颜色分类
    if '主要颜色'  in attrs_name:
        info['主要颜色'] = allattrs['主要颜色']
    else:
        info['主要颜色'] = 'NA'
    if '颜色分类'  in attrs_name:
        info['主要颜色'] = allattrs['颜色分类']
    else:
        info['主要颜色'] = 'NA'

    #尺码
    if '尺码' in attrs_name:
        info['尺码'] = allattrs['尺码']
    else:
        info['尺码'] = 'NA'

    if '组合形式' in attrs_name:
        info['组合形式'] = allattrs['组合形式']
    else:
        info['组合形式'] = 'NA'

    if '裤长' in attrs_name:
        info['裤长'] = allattrs['裤长']
    else:
        info['裤长'] = 'NA'

    return info


import csv

def main():
    # 提取 列
    with open('clothes_detai.csv', 'w', newline='', encoding='utf-8') as csvfile:
        # fieldnames = ['店铺ID','店铺名','链接','宝贝','原价','促销价','月销量','累计评价','材质成分','流行元素','袖长','年份季节','销售渠道类型','货号','服装版型','衣长','领型','袖型',
        #               '裙型','裙长','腰型','裤长','组合形式','品牌','图案','服装款式细节', '适用年龄','风格','通勤','主要颜色','尺码']
        fieldnames=[ 'Link','Brand','Title','Price','Sale price','Sales','Evaluations',
                    'Component', 'Fashion elements','Sleeve','Seasons','Sales channels',
                    'Number','Clothes_Style','Long','Collar type','Sleeve type',
                    'Skirt type','Skirt length','Waist','Combining form','Outseam',
                    'Design','Fashion pattern detail','Applicable age',
                    'Style','Commuter','color','Size']
        #  'Shop','Data_id','Shop_id','Shop','Link','Data_id',
        writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
        writer.writeheader()

        # urls = ['//detail.tmall.com/item.htm?spm=a230r.1.14.1.ebb2eb2eGyUw1&id=549177691667&ns=1&abbucket=4',
                # '//item.taobao.com/item.htm?id=548443640333&ns=1&abbucket=0#detail']

        f = pd.read_csv('women_clothes_sales2.csv')
        urls = f['link'][0:100]
        # sh = f['shop_id'][0:3]
        # s = f['shop'][0:3]
        # for url in urls:
        #     print(url)
        # writer.writerow({'店铺ID':f['shop_id'],'店铺名':f['shop']})
        keys, values = [], []
        # for url in urls:
        for i in urls:
            url = 'http:' + i
            #   endswith  判断字符串是否以指定的字符串结尾
            if url.endswith('detail'):
                info = get_taobao_header(url)

                res = requests.get(url)
                soup = BeautifulSoup(res.text, "html.parser")
                attrs = soup.select('.attributes-list li')   # 淘宝  class
            else:
                info = get_tianmao_header(url)

                res = requests.get(url)
                soup = BeautifulSoup(res.text, "html.parser")
                attrs = soup.select('#J_AttrUL li')  # 天猫 id
                # print('attrs=',attrs)

            d = get_Details(attrs,info)
            print(d)
            # for j in f[shop_id]:
            #     d['店铺ID'] = j
            # for s in f['shop']:
            #     d['店铺名'] = s
            #'Shop':d['店铺名'],'Data_id':d['ID'],
            writer.writerow({'Link':url,'Brand':d['品牌'],'Title':d['宝贝'], 'Price':d['原价'], 'Sale price':d['促销价'], 'Sales':d['月销量'], 'Evaluations':d['累计评价'],
                             'Component':d['材质成分'], 'Fashion elements':d['流行元素'], 'Sleeve':d['袖长'], 'Seasons':d['年份季节'], 'Sales channels':d['销售渠道类型'],
                             'Number':d['货号'],'Clothes_Style':d['服装版型'],'Long':d['衣长'],'Collar type':d['领型'], 'Sleeve type':d['袖型'],
                             'Skirt type':d['裙型'], 'Skirt length':d['裙长'], 'Waist':d['腰型'], 'Combining form':d['组合形式'], 'Outseam':d['裤长'],
                              'Design':d['图案'], 'Fashion pattern detail':d['服装款式细节'],  'Applicable age':d['适用年龄'],
                             'Style':d['风格'], 'Commuter':d['通勤'], 'color':d['主要颜色'], 'Size':d['尺码']})

if __name__=='__main__':
    main()