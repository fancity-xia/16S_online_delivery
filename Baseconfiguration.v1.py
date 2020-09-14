#!/usr/bin/python -w
#-*- coding:utf8 -*-

__author__= 'fancity.xia' 

import os, re, sys, json
from collections import defaultdict
import argparse, subprocess
sys.path.append("/root/16s/Modules/Download_online")
from mysqldatabase import microbase
from mongodb import Mymongo
import datetime
'''
查询mysql和mongo数据库获取需求信息并生成json数据配置文件
'''


class Configuration():

	def __init__(self, analysisid):
		self.analysisid = analysisid
		self.myconfig = {}
		#根据analysis id获取分析路径, 子项目信息, 
		self.search_mongo()
		#根据项目信息获取分析人员, 项目管理, 销售信息; 获取账号密码
		self.search_mysql()


	def search_mysql(self):
		#subid = set()
		self.mysql = microbase("120.24.56.191", "micro16s", 'root', 'BgiMicrobe2020', '3307')
		#查询结果由元组=>dict pymysql.cursors.DictCursor
		self.mysql.to_dict()
		mysearch_password = self.mysql.read_from_outspace('select password from micro16s.t_microbe_customer where customer_email = \"{}\"'.format(self.customer_email))
		self.myconfig.update(mysearch_password[0])
		mysearch = self.mysql.read_from_outspace('select action_man, sale_man, info_email  from micro16s.t_microbe_project \
								where {}'.format(' or '.join("sub_code = \"%s\"" % s for s in self.project)))
		#合并多个项目值
		merge_dict = defaultdict(set)
		print(mysearch)
		for mysearch_element in mysearch:
			for key,value in mysearch_element.items():
				merge_dict[key].add(value)
		
		self.myconfig.update(merge_dict)
		#mysql.pause_database()
	

	def search_mongo(self):
		mymg = Mymongo()
		mymg.connect_mongodb()
		mydb = mymg.mongo_client['microbe']
		collection = mydb.get_collection("analysis.analysis_plan_info")
		findinfo = collection.find_one({'planCode': self.analysisid})
		#if findinfo.get('analysis_path'):
		self.project = findinfo['projects']
		self.customer_email = findinfo.get('customerEmail')
		self.myconfig.update({'analysis_path':findinfo.get('analysis_path', "NULL"), "projects":self.project, "customerEmail": self.customer_email})


	def update_mysql(self, online_account, online_password):
		'''更新关键信息至mysql数据库'''
		self.mysql.read_from_outspace("update micro16s.t_microbe_delivery set add_time='{}',is_upload='1',analysis_path='{}',account='{}', password='{}' where plan_code='{}'".format(str(datetime.datetime.now()), self.myconfig['analysis_path'], online_account, online_password, self.analysisid))


class Onlinepermission():
	'''
	根据customer_email和password 提供/删除/更新 online project 交付账户的下载和查看数据的权限
	'''
	#online_project = set()
	def __init__(self, token="8HX5tDVZIDraS8OS9XSQuTbtaTddT3Qs", bo = "/root/Software/miniconda3/envs/qiime1/bin/bo"):
		self.token = token
		self.bo = bo
		self.login()


	def login(self):
		string  = self.bo + " login --token "  + str(self.token) + " --noprojects"
		self.run_subprocess(string)


	@staticmethod
	def run_subprocess(instring):
		run = subprocess.Popen(instring, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		out, error = run.communicate()
		print(instring)
		error = error.decode('utf8').strip()
		if error:
			#print(instring)
			print(error)
			raise Exception(error)
		return out.decode('utf8').strip()


	def set_delivery(self, customer, password, day="30"):
		'''添加交付账号'''
		string = self.bo + " new delivery_user -p {} -d {} {}".format(password, day, customer)
		self.run_subprocess(string)


	def set_permission(self, online_project, customer):
		'''添加用户权限'''
		string = self.bo + " set_permission -p {} {} dv".format(online_project, customer)
		self.run_subprocess(string)


	def remove_permission(self, online_project, customer):
		'''去除用户权限'''
		string = self.bo + " remove_permission -p {} {} dv".format(online_project, customer)
		self.run_subprocess(string)
		
	
	def update_permission(self, online_project, customer):
		'''更新用户权限'''
		self.remove_permission(online_project, customer)
		self.set_permssion(online_project, customer)
	

	def random_password(self, num=8):
		return ''.join(random.sample(string.ascii_letters + string.digits, num))


	@staticmethod
	def parser_find_format(bo="/root/Software/miniconda3/envs/qiime1/bin/bo"):
		'''
		$bash /root/Software/miniconda3/envs/qiime1/bin/bo  find project
		-----------------------------------------------------------------------
		name                 owner     id
		-----------------------------------------------------------------------
		test1_test2_test3    P_bc_bs   1300eef0-07ac-477c-a016-85dc10131b6f
		Micro16S_Cleandata   P_bc_bs   e99aab0c-b222-472a-ad33-1b7b9b0b592d
		'''
		find_dict = defaultdict(list)
		find_string = bo + " find project"
		find_info = Onlinepermission.run_subprocess(find_string)
		for line in re.split('\n', find_info):
			line = line.strip()
			if re.search('^-', line):
				continue
			lines = re.split('\s+', line)
			find_dict[lines[0]].append(lines[2])
		return find_dict


	def localrecord(self):
		'''
		【本地记录使用的账号密码,方便同一个账户密码重复利用】
		已使用固定账号密码;因此该功能暂停
		'''
		pass



if __name__  == '__main__':
	parser = argparse.ArgumentParser(description='aliyun service machine bo upload cleandata')
	parser.add_argument('--analysisid','-s', required=True, help='analysis id')
	args = parser.parse_args()
	analysisid = args.analysisid
