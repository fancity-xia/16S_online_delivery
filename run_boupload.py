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
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
#sys.path.append("/root/16s/Modules/SimplePipe")
#sys.path.append("/root/16s/Modules")
from Email.exchange_email import Exchange_email
from lib.config import *
from SimplePipe.myRabbitMQ import MyRabbit
import datetime
import subprocess
from delivery_upload import Pipeline_Upload

'''
通过RabbitMQ获取前端json, 上次16S交付数据至online并发送邮件给项目相关人员进行质控; 同时在数据库存储关键信息
多进程处理挂起
'''

class MultiRabbit(MyRabbit):

	MQ_CONFIG = Rabbitmq_delivery_message	
	def __init__(self, exchange, queue, routing_key):
		super(MultiRabbit, self).__init__(exchange, queue, routing_key)
		#self.pool = Pool(5)
		#self.worknum = []


	def callback(self, ch, method, properties, body):
		receive_message = json.loads(body.decode())
		#self.worknum.append(receive_message)
		print(receive_message)
		p = Process(target=Run_mainpipe, args=(receive_message,))
		p.start()


def Run_mainpipe(message):
	try:
		myupload = Pipeline_Upload(message['plan_code'])
		myupload.send_email(message['user_email'])
		myupload.update_mysql()
	except Exception as e:
		errlog = '''<b>Auto Delivery Error</b>:
		<span style="text-indent:2em; color=red">错误日志信息:{} -- {}</span>
		<span style="text-indent:2em; color=green">Connect Email:  {}</span>'''.format(e, message['plan_code'], delivery_online['error_to_adress'])
		Exchange_email(message['plan_code'] + " Micro16S Auto Delivery Debug", errlog, delivery_online['error_to_adress'], message['user_email'])



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
