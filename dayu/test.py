HOST = '120.79.132.229'
PORT = '5672'
USERNAME = "wlwh"
PASSWORD = "Wanglai@123456"

import pika
import json

dayu_data = {
    "id": 0,
    "account": "2313858295@qq.com",
    "password": "chf880302",
    "video_path": r"D:\剪辑片单\1“国民公公”妙答名字由来，知道原因后说：太搞笑了！.mp4",
    "image_path": r"d:\0.png",
    "title": "“国民公公”妙答名字由来，知道原因后说：太搞笑了！",
    "content": "测试测试测试",
    "video_type": "国内",
    "tags": "太热,高分段,发封的是呆"   # 3-6个  必须
}

# toutiao_data = {
#     "id": 0,
#     "account": "212416231@qq.com",
#     "password": "aqsxcc62",
#     "video_path": r"D:\剪辑片单\1“国民公公”妙答名字由来，知道原因后说：太搞笑了！.mp4",
#     "image_path": r"d:\0.png",
#     "title": "“国民公公”妙答名字由来，知道原因后说：太搞笑了！",
#     "content": "测试测试测试",
#     "video_type": "游戏",
#     "tags": "太热,高分段,发封的是呆",
#     "is_origin": 1,           # 原创标记
#     "is_first": 1,            # 首发标记
#     "first_info": {
#         "first_url": "http://www.xxxxx.com",
#         "first_platform": "腾讯",
#         "first_uname": "反反复复"
#     }
# }

# qutoutiao_data = {
#     "id": 0,
#     "account": "15574819298",
#     "password": "yao147258",
#     "video_path": r"D:\剪辑片单\1“国民公公”妙答名字由来，知道原因后说：太搞笑了！.mp4",
#     "image_path": r"d:\0.png",
#     "title": "“国民公公”妙答名字由来，知道原因后说：太搞笑了！",
#     "content": "测试测试测试",
#     "video_type": "国内",
#     "tags": "太热,高分段,发封的是呆"   # 3-6个  必须
# }


# ############################## 生产者 ##############################
user_pwd = pika.PlainCredentials(USERNAME, PASSWORD)
params = pika.ConnectionParameters(HOST, credentials=user_pwd, heartbeat=50, blocked_connection_timeout=300)
connection = pika.BlockingConnection(params)
channel = connection.channel()
# channel.queue_declare(queue='dayu')  # 如果队列没有创建，就创建这个队列
channel.basic_publish(exchange='',
                      routing_key='dayu',   # 指定队列的关键字为，这里是队列的名字
                      body=json.dumps(dayu_data))  # 往队列里发的消息内容
connection.close()
