#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from data_formate import Item
from sqlalchemy import Table,MetaData,create_engine,Column,String,Integer,Boolean,TIMESTAMP,func,Text,Float,BigInteger,UniqueConstraint,SMALLINT,and_,or_,not_,Enum,text
from sqlalchemy.orm import scoped_session,sessionmaker,relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import ForeignKey
import datetime
import pymysql

Base = declarative_base()
DB_CONNECT_STR = "mysql+pymysql://root:duanshihua133@localhost:3306/Crawlers?charset=utf8"
engine = create_engine(DB_CONNECT_STR,echo=False,encoding="utf8",convert_unicode=True)  #已更改为在pipelines中创建
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, 
bind=engine))

# enterprise表与comptype表的多对多中间表
comp_conn_types = Table('comp_conn_types', Base.metadata,
    Column('enterprise_id', BigInteger, ForeignKey('enterprise.id'), nullable=False, primary_key=True),
    Column('comptype_id', Integer, ForeignKey('comptype.id'), nullable=False, primary_key=True)
)

class Site(Base):
	"""
	爬取站点表
	"""
	__tablename__ = 'site'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8'
	}
	id = Column(Integer,primary_key=True,autoincrement=True,comment="主键id")
	code = Column(String(32),nullable=False,comment="竞拍人姓名")
	name = Column(String(32),nullable=False,comment="竞拍人姓名")
	url = Column(String(255),nullable=False,comment="竞拍人姓名")
	crawled_date = Column(TIMESTAMP,nullable=False,default=datetime.datetime.now,comment="站点最后爬取日期")

class Items(Base):
	"""
	项目表
	"""
	__tablename__ = 'item'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8'
	}
	id = Column(BigInteger,primary_key=True,autoincrement=True,comment="项目自增主键id")
	url = Column(String(255),nullable=True,comment="项目拍卖链接")
	title = Column(String(255),nullable=False,index=True,comment="项目标题")
	phase = Column(Enum('一拍','二拍','重新拍卖','变卖','其他'),nullable=False,index=True,server_default='一拍',comment="拍卖阶段：一拍、二拍、重新拍卖、变卖、其他")
	status = Column(Enum('0','1','2','3','4','5'),nullable=False,index=True,server_default='0',comment="项目状态：0:即将开拍,1:正在拍卖,2:结束拍卖,3:拍卖中断,4:取消拍卖,5:其他")
	category = Column(String(32),nullable=False,comment="项目种类,参考category表的值")
	repeat = Column(String(255),index=True,comment="项目去重标志字段")

	province = Column(String(32),nullable=True,comment="省份名")
	city = Column(String(32),nullable=True,comment="城市名")
	county = Column(String(32),nullable=True,comment="县区名")

	images = Column(Text,nullable=True,comment="项目图片")

	starting_price = Column(Float,nullable=True,comment="起拍价格")
	current_price = Column(Float,nullable=True,comment="当前价格")
	appraisal_price = Column(Float,nullable=True,comment="评估价格")
	max_price = Column(Float,nullable=True,comment="当前最高出价")
	deal_price = Column(Float,nullable=True,comment="成交价格")
	margin = Column(Float,nullable=True,comment="保证金")
	markup = Column(Float,nullable=True,comment="加价幅度")
	shipping_fee = Column(String(255),nullable=True,comment="邮费")

	start_time = Column(TIMESTAMP,nullable=True,index=True,comment="开始日期")
	end_time = Column(TIMESTAMP,nullable=True,index=True,comment="结束日期")
	crawled_time = Column(TIMESTAMP,nullable=True,index=True,default=datetime.datetime.now,comment="爬取时间")
	updated_time = Column(TIMESTAMP,nullable=True,index=True,default=datetime.datetime.now,comment="更新时间")
	deal_time = Column(TIMESTAMP,nullable=True,comment="已成交项目竞拍人最后出价的时间")

	people_signed = Column(Integer,nullable=True,comment="预约人数")
	people_alarmed = Column(Integer,nullable=True,comment="设置提醒的人数")
	people_viewed = Column(Integer,nullable=True,comment="查看过的人数")
	people_bid = Column(Integer,nullable=True,comment="已经出价过的人数")

	location = Column(String(255),nullable=True,comment="项目地址")
	area = Column(Float,nullable=True,comment="面积")
	intro = Column(Text,nullable=True,comment="项目介绍")
	other_info = Column(Text,nullable=True,comment="其他项目信息")
	attaches = Column(Text,nullable=True,comment="附件")
	seller = Column(String(255),nullable=True,comment="出售方")
	privileged_people = Column(String(255),nullable=True,comment="优先购买权人")
	bidding_period = Column(String(255),nullable=True,comment="竞价周期,约定该次拍卖的竞价时间如1天表示1天内完成拍卖")
	delay_period = Column(String(255),nullable=True,comment="延时周期,每次出价后的最长等待下次出价的时间")
	court_contacter = Column(String(255),nullable=True,comment="拍卖法院")
	people_contacter = Column(String(255),nullable=True,comment="出让方")
	phone = Column(String(255),nullable=True,comment="联系电话")
	telephone = Column(String(255),nullable=True,comment="联系电话2")
	auction_people = Column(Text,nullable=True,comment="已出价人")

	lng = Column(Float,nullable=True,comment="经度")
	lat = Column(Float,nullable=True,comment="纬度")

	discount = Column(Float,nullable=True,comment="网站折扣率字段")
	code = Column(BigInteger,nullable=True,comment="网站项目编码字段")
	flaw = Column(String(255),nullable=True,comment="网站项目标签栏字段")
	report = Column(Boolean,nullable=False,server_default=text('0'),comment="网站是否可生成报告字段")
	traffic = Column(String(255),nullable=False,server_default='交通全面信息详见电脑版网站地图地理信息',comment="网站项目交通字段")
	school = Column(String(255),nullable=False,server_default='教育学校全面信息详见电脑版网站地图地理信息',comment="网站教育学校字段")
	envir = Column(String(255),nullable=False,server_default='环境配套超市医院健身娱乐银行等全面信息详见电脑版网站地图地理信息',comment="网站环境配套字段")
	contact_phone = Column(String(255),nullable=False,server_default='021-68828928',comment="网站联系电话字段")
	contactor = Column(String(255),nullable=False,server_default='资产信息网 ',comment="网站联系人字段")
	uploaded = Column(Boolean,nullable=True,server_default=text('0'),comment="项目是否已上传到网站服务器")

	extra1 = Column(String(255),nullable=True,comment="预留位1")
	extra2 = Column(String(255),nullable=True,comment="预留位2")
	extra3 = Column(String(255),nullable=True,comment="预留位3")
	extra4 = Column(String(255),nullable=True,comment="预留位4")
	extra5 = Column(String(255),nullable=True,comment="预留位5")

	crawled_times = Column(Integer,nullable=False,server_default=text('0'),comment="已爬取次数,一般最高次数为3次")
	siteId = Column(Integer,ForeignKey('site.id'),nullable=False,comment="项目来源网站id")

	categoryId = Column(Integer,ForeignKey('category.id'),nullable=True,comment="种类id(外键)")

	provinceId = Column(Integer,ForeignKey('province.id'),nullable=True,comment='省份id(外键)')
	cityId = Column(Integer,ForeignKey('city.id'),nullable=True,comment='城市id(外键)')
	countyId = Column(Integer,ForeignKey('county.id'),nullable=True,comment='县区id(外键)')

	industryId_a = Column(Integer,ForeignKey('industry_a.id'),nullable=True,comment='一级行业id')
	industryId_b = Column(Integer,ForeignKey('industry_b.id'),nullable=True,comment='二级行业id')
	industryId_c = Column(Integer,ForeignKey('industry_c.id'),nullable=True,comment='三级行业id')

class Enterprise(Base):
  __tablename__ = 'enterprise'
  __table_args__ = {
	'mysql_engine': 'InnoDB',
	'mysql_charset': 'utf8'
  }
  id = Column(BigInteger,primary_key=True,autoincrement=True,comment='自增主键')
  enterprise = Column(String(255),nullable=False,comment='公司名')
  status = Column(Enum('1','2','3','4','5','6','7','8'),nullable=False,comment='1:在业/存续;2:清算;3:吊销;4:注销;5:停业;6:撤销;7:迁入;8:迁出;')
  represent = Column(String(64),nullable=False,comment='法定代表人')
  regCaps = Column(Float,nullable=True,comment='注册资本,单位:万元')
  payCaps = Column(Float,nullable=True,comment='实缴资本,单位:万元,部分数据源无该属性')
  estabDate = Column(TIMESTAMP,nullable=True,comment='成立日期')
  approveDate = Column(TIMESTAMP,nullable=True,comment='核准日期')

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

class Category(Base):
    """
    项目种类表
    """
    __tablename__ = 'category'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(Integer,primary_key=True,autoincrement=True,comment="项目种类主键")
    category = Column(String(32),nullable=False,comment="种类名")
    code = Column(String(32),nullable=True,comment="网站链接相关编码")
    extra1 = Column(String(255),nullable=True,comment="预留位1")

class Province(Base):
	"""
	省份表
	"""
	__tablename__ = 'province'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8'
	}
	id = Column(Integer,primary_key=True,autoincrement=True,comment="省份id")
	name = Column(String(32),nullable=True,comment='省份')
	simple = Column(String(32),nullable=True,comment='简称')
	code = Column(String(32),nullable=True,comment="网站链接相关编码")
	level = Column(SMALLINT,nullable=True,comment="城市等级")
	extra = Column(String(255),nullable=True,comment="预留位1")

class City(Base):
	"""
	城市表
	"""
	__tablename__ = 'city'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8'
	}
	id = Column(Integer,primary_key=True,autoincrement=True,comment="城市id")
	name = Column(String(32),nullable=True,comment='城市')
	provinceId = Column(Integer,ForeignKey('province.id'),nullable=True,comment="省份id")
	simple = Column(String(32),nullable=True,comment='简称')
	code = Column(String(32),nullable=True,comment="网站链接相关编码")
	level = Column(SMALLINT,nullable=True,comment="城市等级")
	extra = Column(String(255),nullable=True,comment="预留位1")

class County(Base):
	"""
	县区表
	"""
	__tablename__ = 'county'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8'
	}
	id = Column(Integer,primary_key=True,autoincrement=True,comment="县区id")
	name = Column(String(32),nullable=True,comment='县区')
	provinceId = Column(Integer,ForeignKey('province.id'),nullable=True,comment="省份id")
	cityId = Column(Integer,ForeignKey('city.id'),nullable=True,comment="城市id")
	simple = Column(String(32),nullable=True,comment='简称')
	code = Column(String(32),nullable=True,comment="网站链接相关编码")
	extra = Column(String(255),nullable=True,comment="预留位1")

class CompType(Base):
	"""
	公司类型表
	"""
	__tablename__ = 'comptype'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8'
	}
	id = Column(Integer,primary_key=True,autoincrement=True)
	name = Column(String(64),nullable=True,comment='企业类型')

	comps = relationship('Enterprise',secondary=comp_conn_types)

class Industry_a(Base):
  __tablename__ = 'industry_a'
  __table_args__ = {
    'mysql_engine': 'InnoDB',
    'mysql_charset': 'utf8'
  }
  id = Column(Integer,primary_key=True,autoincrement=True)
  name = Column(String(64),nullable=True,comment='一级行业')

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

class Purchaser(Base):
	"""
	项目最后成功竞拍竞拍人信息
	"""
	__tablename__ = 'purchaser'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8'
	}
	id = Column(Integer,primary_key=True,autoincrement=True,comment="主键id")
	name = Column(String(32),nullable=True,comment="竞拍人姓名")
	price = Column(Float,nullable=True,comment="最终成交价")
	confirm_pact = Column(Text,nullable=True,comment="竞拍确认书")

	itemId = Column(BigInteger,ForeignKey('item.id'),nullable=False,comment='项目主键')

class Bid(Base):
	"""
	项目每个出价记录
	"""
	__tablename__ = 'bid'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8'
	}
	id = Column(BigInteger,primary_key=True,autoincrement=True,comment="主键id")
	code = Column(String(32),nullable=True,comment="竞拍编号")
	price = Column(Float,nullable=True,comment="出价")
	bid_time = Column(TIMESTAMP,nullable=True,comment="出价时间")

	itemId = Column(BigInteger,ForeignKey('item.id'),nullable=False,comment='项目主键')

class Cookies(Base):
	"""
	账号信息表
	"""
	__tablename__ = 'cookies'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8'
	}
	id = Column(BigInteger,primary_key=True,autoincrement=True,comment="主键id")
	username = Column(String(255),nullable=False,comment="用户名")
	password = Column(String(255),nullable=False,comment="密码")
	cookie = Column(Text,nullable=True,comment="账号最新cookie")
	phone = Column(String(32),nullable=False,default='',comment="注册手机号")
	useful = Column(Boolean,nullable=False,server_default=text('0'),comment="cookie是否仍可用")
	siteId = Column(Integer,ForeignKey('site.id'),nullable=False,server_default=text('1'),comment="站点id")
	extra = Column(String(255),nullable=True,comment="预留位1")

class Crawl_Log(Base):
	"""
	爬虫日志表
	"""
	__tablename__ = 'crawl_logs'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8'
	}
	id = Column(BigInteger,primary_key=True,autoincrement=True,comment="主键id")
	job = Column(String(255),nullable=True,comment="所执行任务")
	info = Column(String(255),nullable=True,comment="所处理数据")
	exception = Column(Text,nullable=True,comment="错误信息")
	err_level = Column(Integer,nullable=False,server_default=text('0'),comment="错误等级：0:info、1:debug、2:error")
	extra = Column(String(255),nullable=True,comment="预留位1")
	occur_time = Column(TIMESTAMP,nullable=True,index=True,default=datetime.datetime.now,comment="发生时间")
	siteId = Column(Integer,ForeignKey('site.id'),nullable=False,comment="站点id")

def get_items_repeat(siteId, provinceId=None):
    if provinceId:
        all_id = db_session.query(Items.repeat).filter(and_(Items.siteId == siteId, Items.provinceId == provinceId)).all()
    else:
        all_id = db_session.query(Items.repeat).filter(Items.siteId == siteId).all()
    return [i[0] for i in all_id]

def get_update_items():
	now = datetime.datetime.now()
	return db_session.query(Items).filter(and_(Items.status.in_(['0','1']), Items.end_time <= now)).all()

def get_cookies(siteId, useful=True, phone=False):
	if phone:
		return [{'cookie': cookie, 'err_times': 0} for cookie in db_session.query(Cookies).filter(and_(Cookies.siteId == siteId, Cookies.useful == useful, Cookies.phone != '')).all()]
	else:
		return [{'cookie': cookie, 'err_times': 0} for cookie in db_session.query(Cookies).filter(and_(Cookies.siteId == siteId, Cookies.useful == useful)).all()]

def disable_cookie(cookie:dict):
    obj = db_session.query(Cookies).filter(Cookies.id == cookie['cookie'].id).first()
    obj.useful = False
    db_session.commit()

def get_citys():
	return db_session.query(Province).all(), db_session.query(City).all(), db_session.query(County).all()

def main():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    main()
