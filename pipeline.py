from data_formate import Item
from utils.logger import logger
from process import *
import alchemy as db

def process_item(item:Item):
	item.code = get_code(item)
	item.bids = formate_bids(item)
	item.envir = get_envir(item)
	item.school = get_school(item)
	item.report = get_report(item)
	item.traffic = get_traffic(item)
	item.discount = get_discount(item)
	item.contactor = get_contactor(item)
	item.purchaser = formate_purchaser(item)
	item.contact_phone = get_contact_phone(item)
	return item

def process_updated_item(item:db.Item):
	item.bids = formate_bids(item)
	item.updated_time = datetime.datetime.now()
	item.crawled_times += 1
	item.purchaser = formate_purchaser(item)
	item.discount = get_updated_discount(item)
	return item

def upload_item(item:Item):
	# try:
	new_item = db.Items(
		url = item.url,
		title = item.title,
		phase = item.phase,
		status = item.status,
		category = item.category,
		repeat = item.repeat,
		province = item.province,
		city = item.city,
		county = item.county,
		images = item.images,
		starting_price = item.starting_price,
		current_price = item.current_price,
		appraisal_price = item.appraisal_price,
		max_price = item.max_price,
		deal_price = item.deal_price,
		margin = item.margin,
		markup = item.markup,
		shipping_fee = item.shipping_fee,
		start_time = item.start_time,
		end_time = item.end_time,
		updated_time = item.updated_time,
		crawled_time = item.crawled_time,
		deal_time = item.deal_time,
		people_signed = item.people_signed,
		people_alarmed = item.people_alarmed,
		people_viewed = item.people_viewed,
		people_bid = item.people_bid,
		location = item.location,
		area = item.area,
		intro = item.intro,
		attaches = item.attaches,
		seller = item.seller,
		privileged_people = item.privileged_people,
		bidding_period = item.bidding_period,
		delay_period = item.delay_period,
		court_contacter = item.court_contacter,
		people_contacter = item.people_contacter,
		phone = item.phone,
		telephone = item.telephone,
		lng = item.lng,
		lat = item.lat,
		uploaded = item.uploaded,
		extra1 = item.extra1,
		extra2 = item.extra2,
		extra3 = item.extra3,
		extra4 = item.extra4,
		extra5 = item.extra5,
		siteId = item.siteId,
		categoryId = item.categoryId,
		provinceId = item.provinceId,
		cityId = item.cityId,
		countyId = item.countyId,
		industryId_a = item.industryId_a,
		industryId_b = item.industryId_b,
		industryId_c = item.industryId_c
	)
	db.db_session.add(new_item)
	db.db_session.flush()
	for bid in item.bids:
		new_bid = db.Bid(
			code = bid.code,
			price = bid.price,
			bid_time = bid.bid_time,
			itemId = new_item.id
		)
		db.db_session.add(new_bid)
	if item.purchaser.code or item.purchaser.name:
		new_purchaser = db.Purchaser(
			name = item.purchaser.name,
			title = item.purchaser.title,
			code = item.purchaser.code,
			price = item.purchaser.price,
			deal_time = item.purchaser.deal_time,
			itemId = new_item.id
		)
		db.db_session.add(new_purchaser)
	db.db_session.commit()
	# except Exception as e:
	# 	logger.info(f'上传item:{item}时出错:{e}')
	# 	db.db_session.rollback()

def upload_updated_item(item:db.Item):
	try:
		db.db_session.add(item)
		db.db_session.commit()
	except Exception as e:
		logger.info(f'上传item:{item}时出错:{e}')
		db.db_session.rollback()