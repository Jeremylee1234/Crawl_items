
import datetime

class Item(object):
	def __init__(self, repeat, site_id):
		self.id = None # 项目id,自增主键值,int
		self.url = None # 项目源链接,str
		self.title = '' # 项目标题,str
		self.phase = '一拍' # 拍卖阶段,枚举值:'一拍','二拍','重新拍卖','变卖','其他',str
		self.status = '0' # 项目状态,枚举值：0:即将开拍,1:正在拍卖,2:结束拍卖,3:取消拍卖,str
		self.category = None # 项目种类,应为category表中对应项目category_id的分类名,str
		self.repeat = repeat # 用于唯一识别项目的字符串,必需id,str
		self.province = None # 省份名,str
		self.city = None # 城市名,str
		self.county = None # 县区名,str
		self.images = '[]' # 项目图片,为单引号列表转字符串,str
		self.starting_price = None # 起拍价格,单位元,float
		self.current_price = None # 当前价格,单位元,float
		self.appraisal_price = None # 评估价格,单位元,flaot
		self.max_price = None # 最高出价,单位元,float
		self.deal_price = None # 成交价格,单位元,float
		self.margin = None # 保证金,单位元,flaot
		self.markup = None # 加价幅度,单位元,float
		self.shipping_fee = None # 邮费,字符串描述,str
		self.start_time = None # 起拍日期,datetime.datetime
		self.end_time = None # 结束日期,datetime.datetime
		self.updated_time = datetime.datetime.now() # 爬取日期,datetime.datetime
		self.crawled_time = datetime.datetime.now()
		self.deal_time = None # 竞拍成交日期, datetime.datetime
		self.people_signed = None # 关注人数,int
		self.people_alarmed = None # 设置提醒人数,int
		self.people_viewed = None # 点击人数,int
		self.people_bid = None # 出价人数,int
		self.location = None # 项目地址,str
		self.area = None # 房地产类的资产面积,股权债权类的单位为万元的保证金,float
		self.intro = '' # 项目说明,str
		self.other_info = None # 其他项目说明,str
		self.attaches = '[]' # 项目附件,为单引号列表转字符串,str
		self.seller = None # 买方,str
		self.privileged_people = None # 优先购买权人,str
		self.bidding_period = None # 竞价周期,str
		self.delay_period = None # 延时周期,str
		self.court_contacter = None # 法院联系人,str
		self.people_contacter = None # 联系人,str
		self.phone = None # 联系电话,str
		self.telephone = None # 联系电话2,str
		self.auction_people = '[]' # 参拍人员信息,为单引号列表转字符串,str
		self.lng = None # 经度,float
		self.lat = None # 纬度,float
		self.discount = None # 网站折扣率字段
		self.code = None # 网站项目编号字段
		self.flaw = None # 网站项目标签字段
		self.report = None # 网站项目是否可生成报告字段
		self.traffic = None # 网站项目交通字段
		self.school = None # 网站教育学校字段
		self.envir = None # 网站环境配套字段
		self.contact_phone = None # 网站联系电话字段
		self.contactor = None # 网站联系人字段
		self.uploaded = 0 # 项目是否已上传网站,boolean
		self.extra1 = None # 预留位1,str
		self.extra2 = None # 预留位2,str
		self.extra3 = None # 预留位3,str
		self.extra4 = None # 预留位4,str
		self.extra5 = None # 预留位5,str
		self.siteId = site_id # 站点id,必需字段,int
		self.crawled_time = 1 # 已爬取次数
		self.categoryId = None # 种类id,外键,为category表中id值,int
		self.provinceId = None # 省份id,外键,为province表中id值,int
		self.cityId = None # 城市id,外键,为city表中id值,int
		self.countyId = None # 县区id,外键,为county表中id值,int
		self.industryId_a = None # 一级行业id,int
		self.industryId_b = None # 二级行业id,int
		self.industryId_c = None # 三级行业id,int

		self.bids = [] # 存储全部出价记录,需要后续处理
		
class Purchaser(object):
	"""
	项目最后成功竞拍竞拍人信息
	"""
	def __init__(self, itemid, name=None, price=None, confirm_pact=None):
		name = name # 姓名,str
		price = price # 成交价格,str
		confirm_pact = confirm_pact # 竞拍确认书内容
		itemId = itemid # 对应项目id

class Bid(object):
	"""
	竞拍记录内容
	"""
	def __init__(self, itemid, code=None, price=None, bid_time=None):
		code = code # 竞拍编号
		price = price # 竞拍出价
		bid_time = bid_time # 竞拍时间
		itemId = itemid # 对应项目id

class Crawl_Log(object):
	def __init__(self, siteid, job=None, info=None, exception=None, err_level=0):
		self.job = job # 所执行的内容,str
		self.info = info # 附带信息,如请求时的请求url,str
		self.exception = exception # 错误信息,str
		self.err_level = err_level # 错误登记,int
		self.occur_time = datetime.datetime.now() # 错误发生时间,datetime.datetime
		self.siteId = siteid
