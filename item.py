
from utils import utils
import datetime

now = datetime.datetime.now()
default_start = datetime.datetime.now() + datetime.timedelta(days=16)
default_end = datetime.datetime.now() + datetime.timedelta(days=17)

class Item(object):
	def __init__(self, repeat, source):
		self.id = utils.get_id()
		self.url = None
		self.phase = '其他'
		self.title = ''
		self.category = ''
		self.repeat = repeat
		self.province = None
		self.city = None
		self.county = None
		self.images = '[]'
		self.starting_price = None
		self.current_price = None
		self.appraisal_price = None
		self.max_price = None
		self.margin = None
		self.markup = None
		self.shipping_fee = None
		self.start_date = default_start
		self.end_date = None
		self.updated_time = datetime.datetime.now()
		self.people_signed = None
		self.people_alarmed = None
		self.people_viewed = None
		self.people_bid = None
		self.location = None
		self.area = None
		self.intro = ''
		self.other_info = None
		self.attaches = '[]'
		self.seller = None
		self.privileged_people = None
		self.bidding_period = None
		self.delay_period = None
		self.court_contacter = None
		self.people_contacter = None
		self.phone = None
		self.telephone = None
		self.auction_people = '[]'
		self.lng = None
		self.lat = None
		self.source = source
		self.uploaded = 0
		self.extra1 = None
		self.extra2 = None
		self.extra3 = None
		self.extra4 = None
		self.extra5 = None
		self.province_id = None
		self.city_id = None
		self.county_id = None
		self.category_id = 21 #默认为其他