## Micro16S 交互系统online交付

![](./online_upload.png)

#### 后端主程序: 

```shell
python3 /root/16s/Modules/Bo_upload/delivery_upload.py -h
aliyun service machine bo upload cleandata

optional arguments:
  -h, --help            show this help message and exit
  --analysisid ANALYSISID, -s ANALYSISID
                        analysis id
根据analysisid从mysql和mongo数据库查询关键信息(信息分析邮箱,分析路径,项目信息)上传cleandata和部分分析数据至online; 并提供给客户账号密码(账号为邮箱前缀, 密码与16S登录系统一致)发送邮件, 同时把上传成功的状态, online账号密码, 分析路径传递给mysql数据库t_microbe_delivery表。
数据库账号密码需要即使跟随数据库变动而更新！(必须mongo数据库有该分析id的路径)
```

如不需要进行前端交互则可以直接通过该程序输入参数执行, 会发送邮件更新数据库


```shell
/root/16s/Modules/Bo_upload/UploadPure -h
usage: UploadPure [-h] --projectid PROJECTID --analysispath ANALYSISPATH

Upload Deliery-Data To Online

optional arguments:
  -h, --help            show this help message and exit
  --projectid PROJECTID, -p PROJECTID
	                        subproject id
  --analysispath ANALYSISPATH, -a ANALYSISPATH
								analysis upload path
根据指定的analysispath(而不是通过mongo数据库)和analysisid 从mysql获取关键信息上传analysispath下数据至online 并发送邮件通知; 目前暂不传递信息给mysql数据库t_microbe_delivery表
													  
```


![](./email.png)



#### 自动化程序

为实现前端页面一键交付功能对后端主程序进行了包装同时也添加了与前端的消息交互; 前端操作如下：

![](./web.png)

后端分析:

通过后端通过RabbitMQ(指定的交换机和队列)获取前端消息(目前只传递方案编号也叫【analysis id】)；后台通过nohup一直挂在16s服务器中运行(不重启服务器就不会中断)生成日志bo_upload.log; 

目前

RabbitMQ：交互消息的队列 路由 交换机

exchange : DELIVERY

queue : DELIVERY

routing_key : DELIVERY

```
/root/16s/Modules/Bo_upload
python3 run_boupload.py -h
pusage: run_boupload.py [-h] [--exchange EXCHANGE] [--queue QUEUE]
                       [--route ROUTE]

Reading config and producing my html format module by pyh

optional arguments:
  -h, --help            show this help message and exit
  --exchange EXCHANGE, -e EXCHANGE
                        rabbitmq exchange name
  --queue QUEUE, -q QUEUE
                        rabbitmq queue name
  --route ROUTE, -r ROUTE
                        rabbitmq routing_key name

```

日志：

```shell
{'plan_code': '6cLB4ma'}
mongodb://root:BgiMicrobe%402020@120.24.55.116:27017
connect successful......
connect mysql......
connect mysql successful......
[{'action_man': 'zhaoyifan@bgi.com', 'sale_man': 'caidan@genomics.cn', 'info_email': 'zengdan@genomics.cn'}]
/root/Software/miniconda3/envs/qiime1/bin/bo login --token ****** --noprojects
/root/Software/miniconda3/envs/qiime1/bin/bo select V3fmjM
Could not find a project named 'V3fmjM'
V3fmjM need to be created
/root/Software/miniconda3/envs/qiime1/bin/bo new project V3fmjM
/root/Software/miniconda3/envs/qiime1/bin/bo mkdir c1d1004f-1f60-4c60-b9f4-5c686e037a75:/6cLB4ma
/root/Software/miniconda3/envs/qiime1/bin/bo upload -c 5 -f /nas1/production_16s/analysis/report/6cLB4ma/result/upload c1d1004f-1f60-4c60-b9f4-5c686e037a75:/6cLB4ma/
/root/Software/miniconda3/envs/qiime1/bin/bo new delivery_user -p 2vXfofO -d 30 807729670online
/root/Software/miniconda3/envs/qiime1/bin/bo set_permission -p c1d1004f-1f60-4c60-b9f4-5c686e037a75 807729670online dv
```

