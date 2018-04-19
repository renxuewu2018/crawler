#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: renxuewu
# @Email:  seektolive@gmail.com
# @Date:   2018-04-17 10:57:55
# @Last Modified by:   renxuewu
# @Last Modified time: 2018-04-17 16:41:33

import random

proxys = [
	'47.91.139.78:80',
	'112.21.164.58:1080',
	'50.233.137.34:80',
	'50.233.137.38:80',
	'39.134.10.26:8080',
	'39.134.10.14:8080',
	'39.134.10.10:8080',
	'39.134.10.6:8088',
	'39.134.10.3:8088',
	'61.216.96.43:8081'
]

def get_random_proxy():
	return random.choice(proxys)

if __name__ == '__main__':
	print(get_random_proxy())
	ss = '129761人付款'
	print(ss[:-3])