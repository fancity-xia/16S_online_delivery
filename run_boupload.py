#!/root/Software/miniconda3/bin/python3
#-*- coding:utf8 -*-
__author__ = "xiazhanfeng"
__version__ = '1.1'

import os, re, sys
import argparse
import json
import yaml
from multiprocessing import Process
import subprocess
sys.path.append("/root/16s/Modules/SimplePipe")
from myRabbitMQ import MyRabbit
import datetime
import subprocess
from delivery_upload import Online_upload

'''
通过RabbitMQ获取前端json, 上次16S交付数据至online并发送邮件给项目相关人员进行质控; 同时在数据库存储关键信息
多进程处理挂起
'''

class MultiRabbit(MyRabbit):
	
	def __init__(self, exchange, queue, routing_key):
		super(MultiRabbit, self).__init__(exchange, queue, routing_key)
		#self.pool = Pool(5)
		#self.worknum = []


	def callback(self, ch, method, properties, body):
		receive_message = json.loads(body.decode())
		#self.worknum.append(receive_message)
		print(receive_message)
		p = Process(target=Run_mainpipe, args=(receive_message['plan_code'],))
		p.start()


def Run_mainpipe(plan_code):
	try:
		myupload = Online_upload(plan_code)
		myupload.send_email()
		myupload.update_mysql()
	except Exception as e:
		print(e)



if __name__  == '__main__':
	parser = argparse.ArgumentParser(description='Reading config and producing my html format module by pyh')
	parser.add_argument('--exchange','-e', required=False, help='rabbitmq exchange name', default="DELIVERY")
	parser.add_argument('--queue','-q', required=False, help='rabbitmq queue name', default="DELIVERY")
	parser.add_argument('--route','-r', required=False, help='rabbitmq routing_key name', default="DELIVERY")
	args = parser.parse_args()
	exchange = args.exchange
	queue = args.queue
	route = args.route
	rab = MultiRabbit(exchange, queue, route)
	rab.receieve()
