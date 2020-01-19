from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from scrapy.conf import settings

DB_USER = settings.get("DB_USER")
DB_PWD = settings.get("DB_PWD")
DB_HOST = settings.get("DB_HOST")
DB_NAME = settings.get("DB_NAME")
engine = create_engine('mysql+pymysql://%s:%s@%s/%s?charset=utf8&autocommit=true' %
                       (DB_USER, DB_PWD, DB_HOST, DB_NAME),
                       max_overflow=0,  # 超过连接池大小外最多创建的连接
                       pool_size=5,  # 连接池大小
                       pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
                       pool_recycle=-1  # 多久之后对线程池中的线程进行一次连接的回收（重置）
                       )

Base = declarative_base()  # 数据库表基类
SessionFactory = sessionmaker(bind=engine)  # 数据库会话对象
session = scoped_session(SessionFactory)  # 线程本地化存储


class Video(Base):

    __tablename__ = 'td_collect_vedio'

    cvedio_id = Column(BIGINT(20), primary_key=True)
    title = Column(String(100))           # 标题
    type_name = Column(String(20))        # 分类名称
    type_id = Column(BIGINT(20))          # 分类id
    publish_time = Column(DateTime)       # 发布时间
    publish_name = Column(String(50))     # 发布者名字
    hit = Column(BIGINT(20))              # 观看量
    comment_num = Column(BIGINT(20))      # 评论量
    imgurl = Column(String(255))          # 封面图片
    create_time = Column(DateTime)        # 采集时间
    pid = Column(BIGINT(20))              # 平台id     对照表: td_platform
    plat_name = Column(String(50))        # 平台名
    is_reader = Column(BIGINT(5))         # 是否查看
    is_use = Column(BIGINT(5))            # 是否引用
    intro = Column(String(500))           # 简介
    use_num = Column(BIGINT(10))          # 平台使用量
    message_status = Column(String(100))  # 返回状态状态
    message_log = Column(String(255))     # 返回日志
    collect_name = Column(String(50))     # 发布人
    collect_phone = Column(BIGINT(11))    # 发布人手机号
    source_url = Column(String(255))      # 播放地址
    path = Column(String(255))            # 文件路径
    is_index = Column(BIGINT(2))          # 是否索引  固定写1
    did = Column(String(100))             # 类型标识
