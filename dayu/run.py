import json
import time
import logging
import threading
import os
import re
from datetime import datetime

import pika
from db.mysql import TdResourceAccount, session, TdPlatformAccount
from upload.dayuupload import DayuUpload
from upload.qutoutiao import QutoutiaoUpload
from upload.toutiao import ToutiaoUpload
from util import logger
from redis_helper import re_handler
from settings import *


#mq主机配置
HOST = MQ_HOST
PORT = MQ_PORT
USERNAME = MQ_USERNAME
PASSWORD = MQ_PASSWORD


# 大鱼上传视频类型
vtype_set = (
    '社会', '国内', '国际', '体育', '科技', '娱乐', '军事', '财经', '汽车', '房产', '时尚', '健康', '两性情感', '游戏', '动漫', '旅游', '美食', '历史',
    '奇闻',
    '科学探索', '星座', '育儿', '教育', '美女', '搞笑', '演讲', '萌娃', '萌宠', '音乐', '语言类', '记录短片', '涨姿势', '劲爆体育', '幽默', '综艺', '电视剧',
    '电影', '纪录片', '少儿','文化', '三农', '生活方式')

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



def callback_dayu(ch, method, properties, body):
    data = json.loads(body.decode())
    logger.info("获得任务 : {}".format(data))
    can = True       # 校验标识
    acc_flag = False
    # 格式处理
    tag_list = data["tags"].split(",")
    data["tags"] = data["tags"].split(",")
    data["image_path"] = data["image_path"].replace("/", "\\")
    data["video_path"] = data["video_path"].replace("/", "\\")

    # 查询发布状态
    did = data["id"]
    video_type = data["video_type"]
    res = session.query(TdResourceAccount).get(did)
    try:
        acc = session.query(TdPlatformAccount).filter(TdPlatformAccount.login_name == data['account'])
        acc_flag = True
    except Exception:
        pass
    if not res:         # 判断任务是否存在
        logger.error("大鱼任务{} 状态异常 原因: id=>{} 任务不存在 ".format(data, did))
        res.status = 9
        res.remark = '任务不存在'
        re_handler.del_a_key('pubId:' + str(did))
        can = False
    for _ in range(len(tag_list)-1):
        if tag_list[_] == tag_list[_ + 1]:
            logger.info("标签重复，请重新提交")
            res.remark = '标签重复，请重新提交'
            res.status = 9
            re_handler.del_a_key('pubId:' + str(did))
            can = False
    if res.status != 3:         # 判断状态是否允许发布
        logger.error("大鱼任务{} 状态异常 status=> {}| ".format(did, res.status))
        res.remark = "发布状态异常 status=> {}| ".format(res.status) + datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        res.remark = '状态不为3，状态异常'
        re_handler.del_a_key('pubId:' + str(did))
        res.status = 9
        can = False
    if video_type not in vtype_set:        # 判断视频类型
        logger.error("大鱼任务 {} 视频类型错误 =>".format(did, video_type))
        res.remark = "视频类型错误 => {}|".format(video_type) + datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        res.status = 9
        re_handler.del_a_key('pubId:' + str(did))
        can = False
    if can:
        try:
            status, aid, vid, msg, cookies = DayuUpload(**data).run()
            logger.info("当前任务{} status: {}, aid: {}, vid: {}, msg:{}".format(did, status, aid, vid, msg))
        except KeyError:
            logger.error("任务 {} 缺少参数 消息=>{}".format(did, data))
            res.remark = '消息队列参数缺失'
            res.status = 9
            re_handler.del_a_key('pubId:' + str(did))
        except Exception as e:
            logger.error("上传未知错误 任务id:{}  error=>{}".format(did, e))
            res.status = 9
            res.remark = "未知错误 请检查发文日志 任务id {}".format(did) + '|' + datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
            re_handler.del_a_key('pubId:' + str(did))
        else:
            if not status:
                res.status = 9
                if acc_flag:
                    acc.cookies = cookies
                logger.info('发布失败 {}'.format(msg))
                res.remark = '发布失败 {}'.format(msg)
                res.status = 9
                re_handler.del_a_key('pubId:' + str(did))
            else:
                logger.info("id: {} 发布成功".format(did))
                res.remark = '发布成功'
                res.status = 8
                res.article_id = aid
                res.vid = vid
                if acc_flag:
                    acc.cookies = cookies
                re_handler.del_a_key('pubId:' + str(did))
    res.publish_date = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    ch.basic_ack(delivery_tag=method.delivery_tag)
    session.commit()


def callback_qutoutiao(ch, method, properties, body):
    try:
        data = json.loads(body.decode())
        logger.info("获得任务 : {}".format(data))
        time.sleep(300)
        can = True       # 校验标识
        # 数据处理
        data["tags"] = data["tags"].split(",")
        data["image_path"] = data["image_path"].replace("/", "\\")
        data["video_path"] = data["video_path"].replace("/", "\\")
        did = data["id"]
        res = session.query(TdResourceAccount).get(did)
        if re_handler.get_a_key(data['account']):
            ch.basic_ack(delivery_tag=method.delivery_tag)
            ch.basic_publish(exchange='', routing_key='qutoutiao', body=body)
            return
        re_handler.set_a_key(data['account'],'defalt')
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
        res.publish_date = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        session.commit()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        re_handler.del_a_key(data['account'])
    except Exception as e:
        print(e)
    finally:
        re_handler.del_a_key(data['account'])



def callback_toutiao(ch, method, properties, body):
    data = json.loads(body.decode())
    logger.info("获得任务 : {}".format(data))
    did = data["id"]
    can = True       # 校验标识
    acc_flag = False
    # 格式处理
    data["tags"] = data["tags"].split(",")
    data["image_path"] = data["image_path"].replace("/", "\\")
    data["video_path"] = data["video_path"].replace("/", "\\")

    # 校验
    res = session.query(TdResourceAccount).get(did)
    #查看账户是否存在，如果不存在将无法更新cookies
    try:
        acc = session.query(TdPlatformAccount).filter(TdPlatformAccount.login_name == data['account'])
        acc_flag = True
    except Exception:
        pass
    if not res:         # 判断任务是否存在
        logger.error("当前任务{} 状态异常 原因: id=>{} 任务不存在 ".format(data, did))
        res.remark = '任务不存在数据库中，请联系技术人员'
        res.status = 9
        re_handler.del_a_key('pubId:' + str(did))
        can = False
    if res.status != 3:         # 判断状态是否允许发布
        logger.error("头条任务{} 状态异常 status=> {}| ".format(did, res.status))
        res.remark = "发布状态异常 status=> {}| ".format(res.status) + datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        res.status = 9
        re_handler.del_a_key('pubId:' + str(did))
        can = False
    if can:
        try:
            status, aid, vid, msg, cookies = ToutiaoUpload(**data).run()
            logger.info("当前任务{} status: {}, aid: {}, vid: {}, msg:{}".format(did, status, aid, vid, msg))
        except KeyError:
            logger.error("任务 {} 缺少参数 消息=>{}".format(did, data))
            res.remark = '任务参数传递错误'
            res.status = 9
            re_handler.del_a_key('pubId:' + str(did))
        except Exception as e:
            logger.error("上传未知错误 任务id:{}  error=>{}".format(did, e))
            res.remark = "未知错误 请检查发文日志 任务id {}".format(did) + '|' + datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
            res.status = 9
            re_handler.del_a_key('pubId:' + str(did))
        else:
            if not status:
                res.remark = '发布失败，请重新提交'
                res.status = 9
                res.remark = msg + '|' + datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
                re_handler.del_a_key('pubId:' + str(did))
                if acc_flag:
                    acc.cookies = cookies
            else:
                logger.info("id: {} 发布成功".format(did))
                res.remark = '发布成功'
                res.status = 8
                res.article_id = aid
                res.vid = vid
                re_handler.del_a_key('pubId:' + str(did))
                if acc_flag:
                    acc.cookies = cookies
    res.publish_date = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    session.commit()
    ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == '__main__':
    #在此处设置队列名
    try:
        user_pwd = pika.PlainCredentials(USERNAME, PASSWORD)
        params = pika.ConnectionParameters(HOST, credentials=user_pwd,heartbeat=1000, socket_timeout=500)
        s_conn = pika.BlockingConnection(params)
        chan = s_conn.channel()
        chan.basic_qos(prefetch_count=1)
        chan.queue_declare(queue='dayu', durable=True)
        chan.queue_declare(queue='qutoutiao', durable=True)
        chan.queue_declare(queue='toutiao', durable=True)
        #修改发布平台的地方，需要大鱼发文，请注释qutoutiao和头条。其他的同样的操作。
        if DAYU:
            chan.basic_consume('dayu', callback_dayu, False, exclusive=False)
        if QUTOUTIAO:
            chan.basic_consume('qutoutiao', callback_qutoutiao, auto_ack=False)
        if TOUTIAO:
            chan.basic_consume('toutiao', callback_toutiao, False)
        #修改发文平台end。
        # heartbeat = Heartbeat(chan)
        # heartbeat.start()  # 开启心跳线程
        # heartbeat.startHeartbeat()
        chan.start_consuming()
    except Exception as e:
        print(e)
        os.system('python run.py')

