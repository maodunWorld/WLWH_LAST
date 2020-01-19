import json
import logging
import time
from datetime import datetime
import os
import threading
import pika
from db import session, TdResourceAccount, TdPlatformAccount
from  utils import logger
from uper import aqy_uper
from redis_helper import re_handler

#mq配置
HOST = '120.79.132.229'
PORT = '5672'
USERNAME = "wlwh"
PASSWORD = "Wanglai@123456"

#永康写的mq

#童兼写的心跳线程
class Heartbeat(threading.Thread):
    def __init__(self, connection):
        super(Heartbeat, self).__init__()
        self.lock = threading.Lock()
        self.connection = connection
        self.quitflag = False
        self.stopflag = True
        self.setDaemon(True)


    def run(self):
        while not self.quitflag:
            time.sleep(10)
            self.lock.acquire()
            if self.stopflag:
                self.lock.release()
                continue
            try:
                self.connection.process_data_events()
            except Exception as ex:
                logging.warn("Error format: %s" % (str(ex)))
                self.lock.release()
                return
            self.lock.release()


    def startHeartbeat(self):
        self.lock.acquire()
        if self.quitflag == True:
            self.lock.release()
            return
        self.stopflag = False
        self.lock.release()


def callback_aqy(ch, method, properties, body):
    data = json.loads(body.decode())
    logger.info("获得任务 : {}".format(data))
    can = True  # 校验标识
    ac_flag = False

    # 查询发布状态
    did = data["id"]
    res = session.query(TdResourceAccount).get(did)
    try:
        acc = session.query(TdPlatformAccount).filter(TdPlatformAccount.login_name == data['user']).one()
        ac_flag = True
    except Exception:
        pass
    if not res:  # 判断任务是否存在
        logger.error("大鱼任务{} 状态异常 原因: id=>{} 任务不存在 ".format(data, did))
        res.remark = '任务不存在，请联系技术人员'
        res.status = 9
        re_handler.del_a_key('pubId:' + str(did))
        can = False
    if res.status != 3:  # 判断状态是否允许发布
        logger.error("爱奇艺{} 状态异常 status=> {}| ".format(did, res.status))
        res.remark = "发布状态异常 status=> {}| ".format(res.status) + datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
        res.status = 9
        re_handler.del_a_key('pubId:' + str(did))
        can = False
    if len(data['short_title']) > 11:
        logger.info("短标题不允许超过11个字符")
        res.remark = '短标题不允许超过11个字符'
        res.status = 9
        can = False
        re_handler.del_a_key('pubId:' + str(did))
    if len(data['title']) > 30:
        logger.info('标题不允许超过30个字符')
        res.remark = '标题不允许超过30个字符'
        res.status = 9
        can = False
        re_handler.del_a_key('pubId:' + str(did))
    if can:
        try:
            status, msg, cookies = aqy_uper(**data).main()
            logger.info("当前任务{} status:{} msg:{}".format(did, status, msg))
        except KeyError:
            logger.error("任务 {} 缺少参数 消息=>{}".format(did, data))
            res.remark = "缺少参数"
            res.status = 9
            re_handler.del_a_key('pubId:' + str(did))
            return
        except Exception as e:
            logger.error("上传未知错误 任务id:{}  error=>{}".format(did, e))
            res.status = 9
            res.remark = '上传失败， 错误原因{}'.format(e)
            re_handler.del_a_key('pubId:' + str(did))
            return
        if not status:
            print("scheduler上传失败")
            res.status = 9
            if ac_flag:
                acc.cookies = cookies
            res.remark = '上传失败' + str(msg)
            re_handler.del_a_key('pubId:' + str(did))
        else:
            logger.info("id: {} 发布成功".format(did))
            logger.info("删除redis")
            res.remark = "发布成功"
            res.status = 8
            re_handler.del_a_key('pubId:' + str(did))
            if ac_flag:
                acc.cookies = cookies
    res.publish_date = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    session.commit()
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    try:
        user_pwd = pika.PlainCredentials(USERNAME, PASSWORD)
        params = pika.ConnectionParameters(HOST, credentials=user_pwd ,heartbeat=1000, socket_timeout=500)
        s_conn = pika.BlockingConnection(params)
        chan = s_conn.channel()
        chan.basic_qos(prefetch_count=1)
        chan.queue_declare(queue='iqiyi', durable=True)
        chan.basic_consume('iqiyi', callback_aqy, auto_ack=False)
        # heartbeat = Heartbeat(chan)
        # heartbeat.start()  # 开启心跳线程
        # heartbeat.startHeartbeat()
        chan.start_consuming()
    except Exception as e:
        print(e)
        os.system('python scheduler.py')

