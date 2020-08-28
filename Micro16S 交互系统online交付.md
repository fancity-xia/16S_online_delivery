## Micro16S 交互系统online交付

```shell
python3 /root/16s/Modules/Bo_upload/delivery_upload.py -h
aliyun service machine bo upload cleandata

optional arguments:
  -h, --help            show this help message and exit
  --analysisid ANALYSISID, -s ANALYSISID
                        analysis id
根据analysisid从mysql和mongo数据库查询关键信息(信息分析邮箱,分析路径,项目信息)上传cleandata和部分分析数据至online; 并提供给客户账号密码(账号为邮箱前缀, 密码与16S登录系统一致)发送邮件。
```

![](C:\Users\xiazhanfeng\Desktop\email.png)

