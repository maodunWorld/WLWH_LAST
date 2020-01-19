### 依赖
- 安装you-get
- 安装[ffmpeg](https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-20190521-e45e600-win64-static.zip)并添加到系统环境变量中 



### 运行
正式环境下要将此目录下的scrapy.cfg 中 setting => default 改成
wl_spider_video.setting.pro
```
# cmd 当前路径下下
scrapy crawl iqiyi | touku | qqvideo
```

