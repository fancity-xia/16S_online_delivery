#!/root/Software/miniconda3/bin/python3
#-*- coding:utf8 -*-
__author__ = "xiazhanfeng"
__version__ = '1.1'

import os, sys, datetime
import argparse
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from Bo_upload.delivery_upload import Pipeline_Upload
from OTU_Cluster.lib import upload_cleandata_to_file
from Download_online.mysqldatabase import microbase
from lib.config import *
'''
纯过滤数据上传: 改写关键信息获取途径; 并调起online上传模块同时发送邮件
'''

class PureFilter_upload(Pipeline_Upload):
	'''
	继承自流程bo上传工具
	'''
	def __init__(self, projectid, analysis_path):
		#super(PureFilter_upload, self).__init__(projectid, analysis_path)
		self.analysisid = analysisid
		self.upload_dir = analysis_path
		#定义基本信息; usr, online_project, password, upload_dir
		self.baseinfo_search()
		#online上传主流程
		myupload = UploadMain(self.projectid, self.upload_dir)
		self.password = myupload.upload_main("", self.usr, self.password)


	
	def baseinfo_search(self):
		#usr, online_project, password, upload_dir
		mysql = microbase(mysql_manage_16s['server'], mysql_manage_16s['db'], mysql_manage_16s['user'], mysql_manage_16s['password'])
		mysql.to_dict()
		mysearch = mysql.read_from_outspace('select project_num, action_man, sale_man, info_email \
				from micro16s.t_microbe_project where sub_code = \"{}\"'.format(self.analysisid))[0]
		self.usr = self.analysisid + str(datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S"))
		self.password = ""
		self.online_project = mysearch['project_num']
		self.projects = [self.analysisid,]
		self.project_num = [mysearch['project_num'], ]
		self.action_man = [mysearch['action_man'],]
		self.info_email = [mysearch['info_email'],]


def main(argv=None):
	parser = argparse.ArgumentParser(description='Upload-Deliery-Data-To-Online')
	parser.add_argument('--projectid','-p', required=True, help='subproject id')
	parser.add_argument('--analysispath','-a', required=True, help='analysis upload path')
	args = parser.parse_args(argv)
	projectid = args.projectid
	analsysispath = args.analysispath
	#生成copy
	if not os.path.lexists(analsysispath + "/Cleandata"):
		upload_cleandata_to_file.Run_cp_upload(analsysispath , Pure_16S_Pipeline['method'], Pure_16S_Pipeline['upload_CleanData_output_file'])
	handle_upload = PureFilter_upload(projectid, analsysispath)
	handle_upload.send_email()


if __name__  == '__main__':
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('--projectid','-p', required=True, help='subproject id')
	parser.add_argument('--analysispath','-a', required=True, help='PureFilter project analysis path')
	args = parser.parse_args()
	projectid = args.projectid
	analsysispath = args.analysispath
	handle_upload = PureFilter_upload(projectid, analsysispath)
	handle_upload.send_email()
