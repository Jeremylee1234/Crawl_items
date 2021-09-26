#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import Table,MetaData,create_engine,Column,String,Integer,Boolean,TIMESTAMP,func,Text,Float,BigInteger,UniqueConstraint,SMALLINT,and_,or_,not_,Enum,text
from sqlalchemy.orm import scoped_session,sessionmaker,relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import ForeignKey
import datetime
import pymysql
import time

Base = declarative_base()
DB_CONNECT_STR = "mysql+pymysql://root:duanshihua133@localhost:3306/Crawlers?charset=utf8"
engine = create_engine(DB_CONNECT_STR,echo=False,encoding="utf8",convert_unicode=True)  #已更改为在pipelines中创建
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, 
bind=engine))

class Message(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    phone = Column(String(32), nullable=True)
    upload_time = Column(TIMESTAMP, default=datetime.datetime.now, nullable=False)

def get_new_msg():
    watch_times = 0
    while True:
        msg = db_session.query(Message).order_by(Message.upload_time.desc()).first()
        now = datetime.datetime.now()
        timedelta = now - msg.upload_time
        timedelta = timedelta.seconds()
        if timedelta <= 60 and timedelta >= -30:
            return msg.content
        else:
            watch_times += 1
            time.sleep(3)
        if watch_times >= 30:
            return None

def main():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    main()
