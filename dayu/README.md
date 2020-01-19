# 从Python官网下载Python3.7安装包，在安装时候选择add to path, 部署文件随你定  
## 服务启动环境配置  
### cmd进入当前目录输入 pip install -r requirements.txt,等待依赖安装完成。
# 服务启动命令：cmd当前目录输入 python run.py服务启动  
# 服务重启ctrl + c，后python run.py   
#settings.py：配置文件，可以具体配置跑什么发文程序。   

#服务目录说明  
cache: 验证码缓存  
db: 封装mysql操作  
driver: 必须使用提供的webdriver，否则无法通过滑动验证码  
test: 测试文件  
upload: 上传程序  
redis_helper: 封装了redis删除key的操作  
setting: 一些配置文件，如果在249进行部署，请将IS_ONLINE改为True,如果不是IS_ONLINE默认为False  
util: 封装了工具包，包括模拟滑动轨迹和与windows窗口交互。   


