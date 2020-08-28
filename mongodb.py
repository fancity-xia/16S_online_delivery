#!/usr/bin/python -w
#-*- coding:utf8 -*-

__author__= 'xiazhanfeng' 

import os, sys, re, urllib
import argparse
import pymongo
import base64
__author__ =  "fancity.xia"
__version__ = "1.1"

'''
packages Mongodb function
'''


class Mymongo():

	def __init__(self):
		self._parameter()


	def connect_mongodb(self):
		#connect windowns mongodb database
		url = "mongodb://" + self.username + ":" + self.password + "@" + self.host + ":" + self.port
		print(url)
		try:
			self.mongo_client = pymongo.MongoClient(url)
			print("connect successful......")
		except Exception as e:
			print(e)
		
	def load_parameter(self, username, password, host, port):
		#outer parameter 
		self.username = urllib.parse.quote_plus(username)
		self.password = urllib.parse.quote_plus(password)
		self.host = host
		self.port = port
		

	def _parameter(self):
		#Simple Encryption
		self.password = urllib.parse.quote_plus("BgiMicrobe@2020")
		self.username = urllib.parse.quote_plus("root")
		self.host = "120.24.55.116"
		self.port = "27017"
	

	def __decode(self, string):
		return str(base64.b64decode(string), encoding = 'utf8')
	
	#insert/del/motify/find/index database info 
	
	#database add user and password
	
	#database show dbinfo and collections

	def dbname_exist(self, database):
		#if database in self.mongo_client.list_database_names():
		if database in self.mongo_client.list_database_names():
			coll = self.mongo_client[database]
			print("====== database: " + database + " ======")
			print('\n'.join(coll.list_collection_names()))
			return coll
		else:
			print("collections name " + collections + " Non-exists")
			print('\n'.join(self.mongo_client.list_database_names()))
			return ""


	def show_content(self, database, collection, headline = 0):
		'''display database=>collection=>actual column content'''
		if self.dbname_exist(database):
			if self.collection_exist(database, collection):
				coldata = self.collection_exist(database, collection)
				if headline:
					print("============")
					print("database: " + database + "\ncollections: " + collection)
				count = 0
				for line in coldata.find():
					if headline:
						count += 1
						print(line)
						if count == 1:
							break	
			else:
				print("databse named " + database + " had non-existsed " + collection)
		else:
			print("databse named " + database + " had non-existed")


	def collection_exist(self, primary_database, collections):
		dbobject = self.dbname_exist(primary_database)
		if dbobject:
			secondary_database = self.dbobject[primary_database]
			if collections in secondary_database.list_collection_names():
				return secondary_database[collections]
			else:
				print("collections name " + collections + " Non-exists")
			


if __name__  == '__main__':
	parser = argparse.ArgumentParser(description='')
	args = parser.parse_args()
	process = Mymongo()	
	process.show_content()
