### 头条号，大鱼号cookies池系统介绍：  
###  当前目录下 pip install -r requirements.txt ; cd toutiao_dayu_cookies; python updater.py  
##### driver_toutiao
定制chromedriver ，支持75版本的chrome，支持对抗大鱼号反selenium检测  
##### utils  
工具类，其中db_tools.py 使用LazyMysql封装了业务SQL；loginer_tools.py 封装了模拟滑动轨迹方法  
##### toutiao_dayu_cookies   
系统分为loginer和updater, updater调度loginer获取cookies，并更新到数据库中。  
定时任务考虑到项目维护和代码可读，使用阻塞函数sleep  
