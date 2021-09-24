
from data_formate import Item
from utils.logger import logger
import alchemy as db

def process_item(item:Item):
	return item

def upload_item(item:Item):
	try:
		new_item = db.Items(
			id = item.id,
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
			other_info = item.other_info,
			attaches = item.attaches,
			seller = item.seller,
			privileged_people = item.privileged_people,
			bidding_period = item.bidding_period,
			delay_period = item.delay_period,
			court_contacter = item.court_contacter,
			people_contacter = item.people_contacter,
			phone = item.phone,
			telephone = item.telephone,
			auction_people = item.auction_people,
			lng = item.lng,
			lat = item.lat,
			uploaded = item.uploaded,
			extra1 = item.extra1,
			extra2 = item.extra2,
			extra3 = item.extra3,
			extra4 = item.extra4,
			extra5 = item.extra5,
			siteID = item.siteId,
			categoryId = item.categoryId,
			provinceId = item.provinceId,
			cityId = item.cityId,
			countyId = item.countyId,
			industryId_a = item.industryId_a,
			industryId_b = item.industryId_b,
			industryId_c = item.industryId_c
		)
		db.db_session.add(new_item)
		db.db_session.commit()
	except Exception as e:
		logger.info(f'上传item:{item}时出错:{e}')
		db.db_session.rollback()
