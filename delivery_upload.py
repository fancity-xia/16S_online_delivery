#!/usr/bin/python -w
#-*- coding:utf8 -*-

__author__= 'xiazhanfeng' 

import os, re, sys, datetime
from collections import defaultdict
import argparse
import random, string, json
#from Baseconfiguration import Configuration, Onlinepermission, UploadMain
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from lib.config import *
from Email.exchange_email import Exchange_email
from Bo_upload.Baseconfiguration import Configuration, Onlinepermission, UploadMain

'''
根据子项目代码上传cleandata和基础分析结果至online指定目录返回账号密码
'''

class Pipeline_Upload():
	'''
	/root/Software/miniconda3/envs/qiime1/bin/bo
	'''
	def __init__(self, analysisid, analysis_path="Null"):
		self.analysisid = analysisid
		self.upload_dir = analysis_path
		#定义基本信息; usr, online_project, password, upload_dir
		self.baseinfo_search()
		#online上传主流程
		myupload = UploadMain(self.online_project, self.upload_dir)
		self.password = myupload.upload_main(analysisid, self.usr, self.password)
	

	def baseinfo_search(self):
		#查询数据库获取基本信息
		self.baseinfo = Configuration(self.analysisid, self.upload_dir)
		#self.upload_dir = self.baseinfo.myconfig['analysis_path']
		try:
		    self.upload_dir = self.correct_dir(self.baseinfo.myconfig['analysis_path'])
		except Exception as e:
		    print(e)
		    sys.exit(0)
		#根据方案编号生成账号密码
		self.online_project = '_'.join(self.baseinfo.myconfig['projects'])
		self.usreamil = self.baseinfo.myconfig.get("customerEmail", 'test')
		usr_compile = re.compile(r'(^[A-Za-z0-9]+)@')
		self.usr = usr_compile.findall(self.usreamil)[0]  +  str(delivery_online['account_prefix'])
		self.password = self.baseinfo.myconfig.get("password", "test1234") + str(delivery_online['account_prefix'])	
		self.projects = self.baseinfo.myconfig['projects']
		self.project_num = self.baseinfo.myconfig['project_num']
		self.action_man = self.baseinfo.myconfig['action_man']
		self.info_email = self.baseinfo.myconfig['info_email']

	
	def correct_dir(self, indir):
		'''
		定位并纠正上传数据目录
		'''
		indir = os.path.abspath(indir)
		if os.path.isdir(indir):
			if os.path.isdir(indir + "/result/upload"):
				return indir + "/result/upload"
			else:
				raise Exception("Analysis delivery path Non-exists")
		else:
			raise Exception("Analysis path Non-exists")
			

	
	def update_mysql(self):
		self.baseinfo.update_mysql(self.usr, self.password)


	def send_email(self, other=""):
		'''
		发送交付邮件质控给负责人
		'''
		#to = "xiazhanfeng@genomics.cn"
		to = ','.join(self.action_man)
		if other:
			to = to + "," + other
		email_module = delivery_online['email_module']
		ee = open(email_module, 'r')
		eestring = ee.read()
		ee.close()
		#cc = "xiazhanfeng@genomics.cn"
		cc = delivery_online['email_cc_adress'] + "," + ",".join(self.info_email)
		eestring = eestring.format(self.analysisid, ','.join(self.project_num), ','.join(self.projects), self.usr, self.password)
		myemail = Exchange_email("{}数据交付".format(self.analysisid), eestring, to, cc)


if __name__  == '__main__':
	parser = argparse.ArgumentParser(description='aliyun service machine bo upload cleandata')
	parser.add_argument('--analysisid','-s', required=True, help='analysis id')
	parser.add_argument('--analysis_path','-p', required=False, help='analysis id location', default="")
	args = parser.parse_args()
	analysisid = args.analysisid
	analysis_path = args.analysis_path
	p = Pipeline_Upload(analysisid, analysis_path)
	#p.upload_main()
	p.send_email()
	p.update_mysql()
