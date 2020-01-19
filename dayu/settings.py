#如果在249上部署大鱼需要将IS_ONLINE设置为True。由于服务器是win19服务器系统，将无法跑大鱼发文服务，包括头条趣头条
IS_OLINE = False

#在这里设置开关，你想开那个发文服务就把那个设置为True。
#举个例子，只发大鱼的，就把DAYU设为True。其他同样。
DAYU = True
QUTOUTIAO = False
TOUTIAO = False


#MQ主机ip地址配置
MQ_HOST = '120.79.132.229'
MQ_PORT = '5672'
MQ_USERNAME = "wlwh"
MQ_PASSWORD = "Wanglai@123456"


#Mysql 主机配置, 迁移数据库时，请将td_platform_account和td_resource_account原封不动迁移，包括错别字toekn.
DB_USER = "root"
DB_PWD = "Wanglai@123456"
DB_HOST = "120.79.132.229:3306"
DB_NAME = "wlwh"

#Redisz主机配置
REDIS_HOST = '120.79.132.229'
REDIS_PORT = 6379
REDIS_PASSWORD = 'Wanglai@123456'
