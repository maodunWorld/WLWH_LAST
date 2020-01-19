from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.dialects.mysql import BIGINT, LONGTEXT, TINYINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from settings import DB_HOST, DB_NAME, DB_PWD, DB_USER
DB_USER =  DB_USER
DB_PWD = DB_PWD
DB_HOST = DB_HOST
DB_NAME = DB_NAME
engine = create_engine('mysql+pymysql://%s:%s@%s/%s?charset=utf8&autocommit=true' %
                       (DB_USER, DB_PWD, DB_HOST, DB_NAME),
                       max_overflow=0,  # 超过连接池大小外最多创建的连接
                       pool_size=2,  # 连接池大小
                       pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
                       pool_recycle=-1,
                       # 多久之后对线程池中的线程进行一次连接的回收（重置）
                       )

Base = declarative_base()  # 数据库表基类
SessionFactory = sessionmaker(bind=engine)  # 数据库会话对象
session = scoped_session(SessionFactory)  # 线程本地化存储


class TdResourceAccount(Base):
    __tablename__ = 'td_resource_account'

    pub_id = Column(BIGINT(20), primary_key=True)
    rid = Column(BIGINT(20))
    account_id = Column(BIGINT(20))
    type_id = Column(BIGINT(20))
    resource_type = Column(BIGINT(5))
    pid = Column(BIGINT(5))
    plat_name = Column(String(50))
    publish_time = Column(DateTime)
    use_time = Column(DateTime)
    sizes = Column(String(20))
    file_url = Column(String(255))
    content_type = Column(String(20))
    display_content = Column(LONGTEXT)
    image_url = Column(String(255))
    status = Column(BIGINT(5))
    article_id = Column(String(60))
    vid = Column(String(60))
    transaction_id = Column(String(60))
    is_first = Column(BIGINT(255))
    create_id = Column(BIGINT(20))
    create_time = Column(DateTime)
    title = Column(String(255))
    hit = Column(BIGINT(20))
    play_total = Column(BIGINT(20))
    tags = Column(String(255))
    remark = Column(String(2000))
    original_status = Column(BIGINT(5))
    pub_date = Column(DateTime)
    plat_first_link = Column(String(255))
    plat_first_id = Column(BIGINT(5))


class TdPlatformAccount(Base):
    __tablename__ = 'td_platform_account'

    account_id = Column(BIGINT(20), primary_key=True)
    login_name = Column(String(100))
    password = Column(String(255))
    access_token = Column(String(255))
    data_key = Column(String(255))
    openid = Column(String(255))
    appid = Column(String(255))
    pid = Column(BIGINT(20))
    plat_name = Column(String(100))
    create_time = Column(DateTime)
    user_id = Column(String(50))
    status = Column(BIGINT(5))
    user_type = Column(TINYINT(2))
    client_id = Column(String(255))
    client_secret = Column(String(255))
    #toekn 数据库建表的时候打错了，呆纠正
    refresh_toekn = Column(String(255))
    update_time = Column(DateTime)
    account_name = Column(String(50))
    cookies = Column(String(5000))
    error_status = Column(BIGINT(255))
    is_auth = Column(BIGINT(2))
    score = Column(BIGINT(5))
    level = Column(String(10))
    fans = Column(BIGINT(10))
    plat_state = Column(BIGINT(2))
    remake = Column(String(255))
