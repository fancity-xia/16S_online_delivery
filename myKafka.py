#!/root/Software/miniconda3/bin/python3
#-*- coding:utf8 -*-
__author__ = "xiazhanfeng"
__version__ = '1.1'

import os, re, sys
import argparse
import json
from kafka import KafkaConsumer, KafkaProducer
from multiprocessing import Process
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../lib"))
from config import *
'''
kafka 类用于接收和发送队列消息
'''

class MyKafka():
	
	def __init__(self):
		self.config = kafkaconfig()


	def receive(self):
		consumer = KafkaConsumer(self.config.topic,
				sasl_mechanism = "PLAIN",
				security_protocol = 'SASL_PLAINTEXT',
				group_id = self.config.group,
				auto_offset_reset = 'latest',
				api_version = (0,10),
				#latest(for the first time using group) and earliest
				bootstrap_servers = self.config.server, 
				sasl_plain_username = self.config.user,
				sasl_plain_password = self.config.password)

		for message in consumer:
			print(str(message.value))
			#print(str(message.value.decode("utf8")))
			#myprocess = Process(target = run_delivery , args=(message))
			#myprocess.start()


	def send(self, data):
		#data type(dict)
		producer = KafkaProducer(sasl_mechanism="PLAIN",
				value_serializer=lambda m: json.dumps(m).encode(),
				security_protocol='SASL_PLAINTEXT',
				sasl_plain_username = self.config.user,
				sasl_plain_password = self.config.password,
				bootstrap_servers = self.config.server)		
		producer.send(self.config.topic, data)
		producer.flush()

	
	def info2json(self, info):
		return json.dumps(info)


class kafkaconfig():
	
	'''kafka default parameter'''	

	__slot__ =  ["server", "group", "topic", "user", "password"]
	def __init__(self):
		#self.server = ["120.24.56.191:9092","120.24.52.186:9092","120.24.55.116:9092"]
		#self.test_server = ['16s7:9092','16s7:9093','16s7:9094']
		self.server = Kafka_delivery_message['server']
		self.group = Kafka_delivery_message['group']
		self.topic = Kafka_delivery_message['topic']
		self.user = Kafka_delivery_message['user']
		self.password = Kafka_delivery_message['password']


if __name__  == '__main__':
		parser = argparse.ArgumentParser(description='kafka send or receive info')
		parser.add_argument('--send','-s', required=False, help='whether send info', action = 'store_true')
		parser.add_argument('--receive','-r', required=False, help='whether receive info', action = 'store_true')
		parser.add_argument('--info','-i', required=False, help='send info', default = "Non-Info")
		args = parser.parse_args()
		send = args.send
		receive = args.receive
		info = args.info
		circle = MyKafka()
		if send:
			circle.send(info)
		elif receive:
			circle.receive()
