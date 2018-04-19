#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: renxuewu
# @Email:  seektolive@gmail.com
# @Date:   2018-04-17 10:57:55
# @Last Modified by:   renxuewu
# @Last Modified time: 2018-04-18 17:31:43

import random

proxys = [
	'121.121.125.55:80',
	'175.0.208.239:8060',
	'39.134.10.20:8080',
	'39.134.10.4:8080',
	'114.101.134.224:61234'
]

proxys1=[
	{'http':'121.121.125.55:80'},
	{'http':'175.0.208.239:8060'},
	{'http':'114.101.134.224:61234'},
	{'http':'39.134.10.4:8080'},
	{'http':'39.134.10.4:8080'}
]

def get_random_proxy():
	return random.choice(proxys)

def get_random():
	return random.choice(proxys1)
