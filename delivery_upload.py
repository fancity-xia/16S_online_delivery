#!/usr/bin/python -w
#-*- coding:utf8 -*-

__author__= 'xiazhanfeng' 

import os, re, sys, datetime
from collections import defaultdict
import argparse
import random, string, json
from Baseconfiguration import Configuration, Onlinepermission
sys.path.append("/root/16s/Modules")
from Email.exchange_email import Exchange_email

'''
根据子项目代码上传cleandata和基础分析结果至online指定目录返回账号密码
'''


class Online_upload():
	'''
	/root/Software/miniconda3/envs/qiime1/bin/bo
	'''
	def __init__(self, analysisid, bo = "/root/Software/miniconda3/envs/qiime1/bin/bo"):
		self.analysisid = analysisid
		self.bo = bo
		#查询数据库获取基本信息
		self.baseinfo = Configuration(analysisid)
		#self.upload_dir = self.baseinfo.myconfig['analysis_path']
		try:
			self.upload_dir = self.correct_dir(self.baseinfo.myconfig['analysis_path'])
		except Exception as e:
			print(e)
			sys.exit(0)
		self.online_project = '_'.join(self.baseinfo.myconfig['projects'])
		#登录online 创建账号
		self.online = Onlinepermission()
		print(self.baseinfo.myconfig)
		self.usreamil = self.baseinfo.myconfig.get("customerEmail", 'test')
		usr_compile = re.compile(r'(^[A-Za-z0-9_]+)@')
		self.usr = usr_compile.findall(self.usreamil)[0]
		print(self.usr)
		self.password = self.baseinfo.myconfig.get("password", "test1234")
		#self.upload_main()

	
	def bo_select(self):
		'''需要提前判断project是否存在,并match出keyid'''
		select_string = self.bo + " select " + self.online_project
		try:
			select_info = self.run_subprocess(select_string)
		except Exception as e:
			select_info = e
		print(select_info)
		if select_info == "Could not find a project named '{}'".format(self.online_project):
			print(self.online_project + " need to be created")
			self.create_project()
			#self.remove_permission()
		elif select_info == "Setting current project to: {}".format(self.online_project):
			print(self.online_project + " have existed")
			#针对已有的项目获取其keyid
			keydict = Onlinepermission.parser_find_format()
			#print(keydict)
			#print(self.online_project)
			self.keyid = keydict[self.online_project][0]
		else:
			print("bo updating... or Other error; Exit()")
			sys.exit()


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
			


	def upload_main(self):
		'''
		bo mkdir ...
		bo upload ...
		bo new delivery_user
		bo set_permission
		'''
		# acquire keyid
		self.bo_select()
		#main
		main_step1 = "{} mkdir {}:/{}".format(self.bo, self.keyid, self.analysisid)
		step1_info = self.run_subprocess(main_step1)
		#if step1_info == "create folder success: /{}/".format(self.analysis):
		main_step2 = "{} upload -c {} -f {} {}:/{}/".format(self.bo, str(5), self.upload_dir, self.keyid, self.analysisid)
		step2_info = self.run_subprocess(main_step2)
		#创建交付账号, 默认30天
		self.online.set_delivery(self.usr, self.password)
		#给予d-download v-view
		self.online.set_permission(self.keyid, self.usr)
	

	def create_project(self):
		string  = self.bo + " new project " + self.online_project
		std = self.run_subprocess(string)
		std_match = re.compile(r'[A-Za-z0-9\-\_\/]+$')
		#ProjectID: 1300eef0-07ac-477c-a016-85dc10131b6f
		self.keyid = std_match.findall(std)[0]


	def run_subprocess(self, instring):
		return Onlinepermission.run_subprocess(instring)
		

	def send_email(self):
		'''
		发送交付邮件质控给负责人
		'''
		email_module = "/root/16s/Modules/Bo_upload/email_module.txt"
		ee = open(email_module, 'r')
		eestring = ee.read()
		ee.close()
		#cc = "xiazhanfeng@genomics.cn,wangshuang3@genomics.cn"
		cc = "xiazhanfeng@genomics.cn,wangshuang3@genomics.cn" + ",".join(self.baseinfo.myconfig['info_email'])
		eestring = eestring.format(self.analysisid, ','.join(self.baseinfo.myconfig['projects']), self.usr, self.password)
		myemail = Exchange_email("{}数据交付".format(self.analysisid), eestring, ','.join(self.baseinfo.myconfig['action_man']), cc)


if __name__  == '__main__':
	parser = argparse.ArgumentParser(description='aliyun service machine bo upload cleandata')
	parser.add_argument('--analysisid','-s', required=True, help='analysis id')
	args = parser.parse_args()
	analysisid = args.analysisid
	p = Online_upload(analysisid)
	p.send_email()
