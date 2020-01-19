import json
import os
import re
from datetime import datetime

import pika
from db.mysql import TdResourceAccount, session, TdPlatformAccount
from qutoutiao import  QutoutiaoUpload
from util import logger
from redis_helper import re_handler


HOST = '120.79.132.229'
PORT = '5672'
USERNAME = "wlwh"
PASSWORD = "Wanglai@123456"

#永康写的mq
user_pwd = pika.PlainCredentials(USERNAME, PASSWORD)
params = pika.ConnectionParameters(HOST, credentials=user_pwd, heartbeat=0)
s_conn = pika.BlockingConnection(params)
chan = s_conn.channel()
chan.queue_declare(queue='qutoutiao', durable=True)



def callback_qutoutiao(ch, method, properties, body):
    data = json.loads(body.decode())
    logger.info("获得任务 : {}".format(data))
    ch.basic_ack(delivery_tag=method.delivery_tag)
    can = True       # 校验标识
    # 数据处理
    data["tags"] = data["tags"].split(",")
    data["image_path"] = data["image_path"].replace("/", "\\")
    data["video_path"] = data["video_path"].replace("/", "\\")
    did = data["id"]
    res = session.query(TdResourceAccount).get(did)
    if not res:         # 判断任务是否存在
        logger.error("趣头条任务{} 状态异常 原因: id=>{} 任务不存在 ".format(data, did))
        res.status = 9
        re_handler.del_a_key('pubId:' + str(did))
        can = False
    if res.status != 3:         # 判断状态是否允许发布
        logger.error("趣头条任务{} 状态异常 status=> {}| ".format(did, res.status))
        res.remark = "发布状态异常 status=> {}| ".format(res.status) + datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        res.status = 9
        re_handler.del_a_key('pubId:' + str(did))
        can = False
    if can:
        try:
            status, aid, vid, msg = QutoutiaoUpload(**data).run()
            logger.info("当前任务{} status: {}, aid: {}, vid: {}, msg:{}".format(did, status, aid, vid, msg))
        except KeyError:
            logger.error("任务 {} 缺少参数 消息=>{}".format(did, data))
            res.status = 9
            re_handler.del_a_key('pubId:' + str(did))
            return
        except Exception as e:
            logger.error("上传未知错误 任务id:{}  error=>{}".format(did, e))
            res.status = 9
            res.remark = "未知错误 请检查发文日志 任务id {}".format(did) + '|' + datetime.strftime(datetime.now(),
                                                                                      "%Y-%m-%d %H:%M:%S")
            re_handler.del_a_key('pubId:' + str(did))
        else:
            if not status:
                res.status = 9
                res.remark = '发布失败'
                re_handler.del_a_key('pubId:' + str(did))
            else:
                logger.info("id: {} 发布成功".format(did))
                res.remark = '发布成功'
                res.status = 8
                res.article_id = aid
                res.vid = vid
                re_handler.del_a_key('pubId:' + str(did))
    session.commit()


if __name__ == '__main__':
    #在此处设置队列名
    chan.basic_consume('qutoutiao', callback_qutoutiao, False)
    chan.start_consuming()

