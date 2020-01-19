### 安装python3.7，勾选add to path，进入cmd， 当前目录，输入命令 pip install -r requirements.txt  
###　启动或者重启服务  
##  启动： python scheduler.py  
## 重启: ctrl+c ,后启动
## chromedriver 版本75版本， chrome版本75
# 爱奇艺号视频发文脚本  
##主要package selenium redis sqlalchemny pymysql corlorlog  

### 入口文件  
python scheduler.py  
### scheduler.py 
使用pika链接mq， 调度uper，进行视频上传  

### uper  
视频上传脚本  

### db.py redis_helper.py utils.py  
封装mysql数据库、redis和logger配置