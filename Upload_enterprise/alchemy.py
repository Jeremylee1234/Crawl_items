#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import Table,MetaData,create_engine,Column,String,Integer,Boolean,TIMESTAMP,func,Text,text,Float,BigInteger,SmallInteger,DateTime,UniqueConstraint,and_,or_,not_
from sqlalchemy.orm import scoped_session,sessionmaker,relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import ForeignKey
import pymysql

Base = declarative_base()
server = '81.68.195.64'
username = '' # 已删除
password = '' # 已删除
database = 'RegCustomer'
DB_CONNECT_STR = f'mysql+pymysql://{username}:{password}@{server}:3306/{database}?charset=utf8'
engine = create_engine(DB_CONNECT_STR,echo=False,encoding='utf8')
db_session = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))


# enterprise表与comptype表的多对多中间表
comp_conn_types = Table('comp_conn_types', Base.metadata,
    Column('enterprise_id', Integer, ForeignKey('enterprise.id'), nullable=False, primary_key=True),
    Column('comptype_id', Integer, ForeignKey('comptype.id'), nullable=False, primary_key=True)
)

# class Comp_conn_Types(Base):
#   __tablename__ = 'comp_conn_types'
#   __table_args__ = {
#     'mysql_engine': 'InnoDB',
#     'mysql_charset': 'utf8'
#   }
#   enterprise_id = Column(Integer, ForeignKey('enterprise.id'), primary_key=True),
#   comptype_id = Column(Integer, ForeignKey('comptype.id'), primary_key=True)

class Enterprise(Base):
  __tablename__ = 'enterprise'
  __table_args__ = {
    'mysql_engine': 'InnoDB',
    'mysql_charset': 'utf8'
  }
  id = Column(Integer,primary_key=True,autoincrement=True,comment='自增主键')
  enterprise = Column(String(255),nullable=False,comment='公司名')
  status = Column(SmallInteger,nullable=False,comment='1:在业/存续;2:清算;3:吊销;4:注销;5:停业;6:撤销;7:迁入;8:迁出;')
  represent = Column(String(255),nullable=False,comment='法定代表人')
  regCaps = Column(Float,nullable=True,comment='注册资本,单位:万元')
  payCaps = Column(Float,nullable=True,comment='实缴资本,单位:万元,部分数据源无该属性')
  estabDate = Column(DateTime,nullable=True,comment='成立日期')
  approveDate = Column(DateTime,nullable=True,comment='核准日期')

  operatePeriod = Column(Integer,nullable=True,comment="营业期限,单位:天,无固定期限:0,部分数据源无该属性")
  creditCode = Column(String(18),nullable=True,comment="统一社会信用代码")
  taxpayerCode = Column(String(18),nullable=True,comment="纳税人识别号")
  regCode = Column(String(15),nullable=True,comment="注册号")
  orzCode = Column(String(11),nullable=True,comment="组织机构代码")
  insuranceNum = Column(Integer,nullable=False,server_default=text('0'),comment="参保人数")
  
  emails = Column(String(255),nullable=False,server_default='',comment='联系邮箱,以字符串加逗号分隔来表示全部联系邮箱')
  phones = Column(String(255),nullable=False,server_default='',comment='联系电话,以字符串加逗号分隔来表示全部联系电话')
  formerName = Column(String(255),nullable=True,comment='曾用名')
  engName = Column(String(255),nullable=True,comment='英文名')
  website = Column(String(255),nullable=True,comment='网址')
  address = Column(String(255),nullable=True,comment='企业地址')
  latestAddr = Column(String(255),nullable=True,comment='最新年报地址')
  scopes = Column(Text,nullable=True,comment='经营范围,字符串形式')

  compTypes = relationship('CompType',secondary=comp_conn_types)
  compTypes_content = Column(Text,nullable=True,comment='企业类型,字符串列表形式,逗号分隔')

  provinceId = Column(Integer,ForeignKey('province.id'),nullable=True,comment='省份id')
  cityId = Column(Integer,ForeignKey('city.id'),nullable=True,comment='城市id')
  countyId = Column(Integer,ForeignKey('county.id'),nullable=True,comment='县区id')

  industryId_a = Column(Integer,ForeignKey('industry_a.id'),nullable=True,comment='一级行业id')
  industryId_b = Column(Integer,ForeignKey('industry_b.id'),nullable=True,comment='二级行业id')
  industryId_c = Column(Integer,ForeignKey('industry_c.id'),nullable=True,comment='三级行业id')

class CompType(Base):
  __tablename__ = 'comptype'
  __table_args__ = {
    'mysql_engine': 'InnoDB',
    'mysql_charset': 'utf8'
  }
  id = Column(Integer,primary_key=True,autoincrement=True)
  name = Column(String(255),nullable=True,comment='企业类型')

  comps = relationship('Enterprise',secondary=comp_conn_types, overlaps="compTypes")

class Province(Base):
  __tablename__ = 'province'
  __table_args__ = {
    'mysql_engine': 'InnoDB',
    'mysql_charset': 'utf8'
  }
  id = Column(Integer,primary_key=True,autoincrement=True)
  name = Column(String(255),nullable=True,comment='省份')

class City(Base):
  __tablename__ = 'city'
  __table_args__ = {
    'mysql_engine': 'InnoDB',
    'mysql_charset': 'utf8'
  }
  id = Column(Integer,primary_key=True,autoincrement=True)
  name = Column(String(255),nullable=True,comment='城市')
  provinceId = Column(Integer,ForeignKey('province.id'),nullable=True)

class County(Base):
  __tablename__ = 'county'
  __table_args__ = {
    'mysql_engine': 'InnoDB',
    'mysql_charset': 'utf8'
  }
  id = Column(Integer,primary_key=True,autoincrement=True)
  name = Column(String(255),nullable=True,comment='县区')
  provinceId = Column(Integer,ForeignKey('province.id'),nullable=True)
  cityId = Column(Integer,ForeignKey('city.id'),nullable=True)

class Industry_a(Base):
  __tablename__ = 'industry_a'
  __table_args__ = {
    'mysql_engine': 'InnoDB',
    'mysql_charset': 'utf8'
  }
  id = Column(Integer,primary_key=True,autoincrement=True)
  name = Column(String(255),nullable=True,comment='一级行业')

class Industry_b(Base):
  __tablename__ = 'industry_b'
  __table_args__ = {
    'mysql_engine': 'InnoDB',
    'mysql_charset': 'utf8'
  }
  id = Column(Integer,primary_key=True,autoincrement=True)
  name = Column(String(255),nullable=True,comment='二级行业')
  id_a = Column(Integer,ForeignKey('industry_a.id'),nullable=False)

class Industry_c(Base):
  __tablename__ = 'industry_c'
  __table_args__ = {
    'mysql_engine': 'InnoDB',
    'mysql_charset': 'utf8'
  }
  id = Column(Integer,primary_key=True,autoincrement=True)
  name = Column(String(255),nullable=True,comment='三级行业')
  id_a = Column(Integer,ForeignKey('industry_a.id'),nullable=False)
  id_b = Column(Integer,ForeignKey('industry_b.id'),nullable=False)

def main():
  Base.metadata.create_all(engine)

def get_areas():
  prov_data = db_session.query(Province).all()
  city_data = db_session.query(City).all()
  county_data = db_session.query(County).all()
  all_province = { i.name: (i.id, None, None) for i in prov_data }
  all_city = { i.name: (i.provinceId, i.id, None) for i in city_data }
  all_county = { i.name: (i.provinceId, i.cityId, i.id) for i in county_data }
  return all_province, all_city, all_county

def get_industry():
  indust_a = db_session.query(Industry_a).all()
  indust_b = db_session.query(Industry_b).all()
  indust_c = db_session.query(Industry_c).all()
  return {
    'a': { i.name: (i.id, None, None) for i in indust_a },
    'b': { i.name: (i.id_a, i.id, None) for i in indust_b },
    'c': { i.name: (i.id_a, i.id_b, i.id) for i in indust_c }
  }

def get_compTypes():
  all_compTypes = db_session.query(CompType).all()
  return {
    comptype.name: comptype for comptype in all_compTypes
  }

def get_top_id():
  return db_session.query(func.max(Enterprise.id)).scalar()

if __name__ == '__main__':
    main()