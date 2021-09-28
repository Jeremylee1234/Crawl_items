from selenium.common.exceptions import TimeoutException
from crawlers.taobao.verify import update_all_cookies
from pipeline import *
from utils.create_driver import Driver
from utils.config import global_config
from urllib.request import quote
from utils.logger import logger
from data_formate import Item
from utils import utils,consts
from lxml import etree
import alchemy as db
import demjson
import random
import time
import re

CHANGE_ACCOUNT_LEVEL = int(global_config.get('config','change_account_level'))
DISABLE_ACCOUNT_LEVEL = int(global_config.get('config','disable_account_levle'))
SLEEP_SECONDS = int(global_config.get('config','sleep_seconds'))
SITE_ID = 1

class Get_urls(object):
	def __init__(self, repeat_set) -> None:
		self.err_times = 0
		self.repeat_set = repeat_set

	def access_page(self, province, category, page, driver=None):
		"""
		创建浏览器窗口并尝试访问执行一级页面,
		返回值:
		None:创建失败,请后续处理跳过None
		driver:创建成功
		"""
		if not driver:
			driver = Driver('https://sf.taobao.com/').create_driver() # 此后需要修改为need_proxy及css禁用
		if self.err_times <= 5:
			if driver == None:
				# 判断在多次尝试创建浏览器窗口后失败
				self.err_times = 0
				return None
			url = 'https://sf.taobao.com/item_list.htm?category=' + category[2] + '&auction_source=0&province=' + quote(province[0], encoding='gbk') + '&st_param=4&auction_start_seg=-1&page=' + str(page)
			try:
				if url != driver.current_url:
					driver.get(url)
				if '阿里拍卖' in driver.title:
					# 判断跳转到正常一级页面
					self.err_times = 0
					return driver
				elif '我喜欢' in driver.title:
					# 判断跳转到登陆界面
					self.err_times += 1
					driver.quit()
					return self.access_page(province, category, page)
				elif not utils.isElementExist(driver, '//div'):
					# 判断网络问题页面加载失败
					self.err_times += 1
					driver.quit()
					return self.access_page(province, category, page, driver)
				else:
					# 其他未知错误
					self.err_times += 1
					driver.quit()
					return self.access_page(province, category, page)
			except TimeoutException:
				# 判断浏览器加载超时,作正常页面处理
				if '阿里拍卖' in driver.title:
					# 判断跳转到正常一级页面
					self.err_times = 0
					return driver
				elif '我喜欢' in driver.title:
					# 判断跳转到登陆界面
					self.err_times += 1
					driver.quit()
					return self.access_page(province, category, page)
				elif not utils.isElementExist(driver, '//div'):
					# 判断网络问题页面加载失败
					self.err_times += 1
					driver.quit()
					return self.access_page(province, category, page, driver)
				else:
					# 其他未知错误
					self.err_times += 1
					driver.quit()
					return self.access_page(province, category, page)
			except Exception as e:
				# 其他错误,处理错误
				logger.info(SITE_ID,'访问ali-sf二级页面',e,url)
				self.err_times += 1
				driver.quit()
				return self.access_page(province, category, page)
		else:
			self.err_times = 0
			driver.quit()
			logger.error(SITE_ID,'放弃访问ali-sf二级页面',None,f'province:{province},category:{category},page:{page}')
			return None

	def parse_urls(self, province, category, driver):
		if driver == None:
			return []
		else:
			try:
				pattern_sf = re.compile(r'^.*sf-item.taobao.com/sf_item/([0-9]+).htm/?.*?$')
				results = []
				datas = driver.find_elements_by_xpath('//div[@class="sf-item-list"]/ul[1]/li/a')
				for data in datas:
					try:
						item = Item(str(re.match(pattern_sf, data.get_attribute('href')).group(1)), SITE_ID)
						item.url = data.get_attribute('href')
						item.title = utils.clean(utils.get_attribute(data, './div[contains(@class,"header-section")]/p', 'textContent'))
						item.status = utils.get_int(utils.get_status(data.find_elements_by_xpath('./div[contains(@class,"flag-section")]/div')))
						if item.status in ['2', '3', '4', '5']:
							item.current_price = utils.get_money(utils.get_attribute(data, './div[contains(@class,"info-section")]/p[2]/span[contains(@class,"value")]/em[2]', 'textContent'))
						else:
							item.starting_price = utils.get_money(utils.get_attribute(data, './div[contains(@class,"info-section")]/p[4]/span[contains(@class,"value")]/em[2]', 'textContent'))
						item.appraisal_price = utils.get_money(utils.get_attribute(data, './div[contains(@class,"info-section")]/p[4]/span[contains(@class,"value")]/em[2]', 'textContent'))

						item.people_signed = utils.get_int(utils.get_attribute(data, './div[contains(@class,"footer-section")]/p[2]/em', 'textContent'))
						item.people_viewed = utils.get_int(utils.get_attribute(data, './div[contains(@class,"footer-section")]/p[1]/em', 'textContent'))
						item.category = category[0]
						item.categoryId = category[3]
						item.province = province[0]
						item.provinceId = province[1]
						if not item.repeat in self.repeat_set:
							self.repeat_set.append(item.repeat)
							results.append(item)
					except Exception as e:
						logger.error(SITE_ID,f'解析ali-sf二级页面某项',e,driver.current_url)
						continue
				driver.quit()
				return results
			except Exception as e:
				logger.error(SITE_ID,f'解析ali-sf二级页面',e,driver.current_url)
				return []

class Parse_detail(object):
	def __init__(self) -> None:
		self.err_times = 0
		self.correct_count = 0
		self.useful_cookies = db.get_cookies(SITE_ID,True)

		if len(self.useful_cookies) >= 1:
			self.cookie_obj = random.choice(self.useful_cookies)
			self.cookie = utils.format_sele_cookies(self.cookie_obj['cookie'].cookie)
			self.session = utils.get_session(utils.process_headers(consts.sf_pc_detail_headers), self.cookie)
		else:
			update_all_cookies()
			self.useful_cookies = db.get_cookies(SITE_ID,True)
			self.cookie_obj = random.choice(self.useful_cookies)
			self.cookie = utils.format_sele_cookies(self.cookie_obj['cookie'].cookie)
			self.session = utils.get_session(utils.process_headers(consts.sf_pc_detail_headers), self.cookie)

	def parse_detail(self, item:Item):
		if self.err_times <= 2:
			try:
				response = self.session.get(url=item.url)
				if response.status_code == 200:
					selector = etree.HTML(response.text)
					item.phase = utils.get_phase(utils.clean(utils.outFirst(selector.xpath('//span[@class="item-status"]/text()'))))
					item.images = str(['https:' + url for url in selector.xpath('//ul[@id="J_UlThumb"]//img/@src')])
					item.current_price = utils.get_money(utils.outFirst(selector.xpath('//span[contains(@class,"current-price")]/em/text()')))
					if item.status in ['2', '3', '4', '5']:
						item.deal_price = item.current_price
					item.people_contacter = utils.clean(utils.list_to_str(selector.xpath('//div[contains(@class,"contact-unit")]//text()')))
					item.location = utils.clean(utils.list_to_str(selector.xpath('//div[contains(@class,"item-address")]//text()')))
					item.lng, item.lat = utils.parse_coordinate(utils.outFirst(selector.xpath('//input[@id="J_Coordinate"]/@value')))
					item.start_time = utils.formate_timestamp(utils.outFirst(selector.xpath('//li[@id="sf-countdown"]/@data-start')))
					item.end_time = utils.formate_timestamp(utils.outFirst(selector.xpath('//li[@id="sf-countdown"]/@data-end')))
					item.seller = utils.clean(utils.list_to_str(selector.xpath('//div[contains(@class,"subscribe-unit")][1]/span[2]//text()')))
					item.court_contacter = utils.clean(utils.list_to_str(selector.xpath('//div[contains(@class,"subscribe-unit")][2]/span[2]//text()')))
					item.people_contacter = utils.clean(utils.outFirst(selector.xpath('//em[contains(@class,"contact-unit-person")]//text()')))
					item.phone = utils.clean(utils.list_to_str(selector.xpath('//p[contains(@class,"contact-line")][1]/span[2]//text()')))
					item.telephone = utils.clean(utils.list_to_str(selector.xpath('//p[contains(@class,"contact-line")][2]/span[2]//text()')))
					infos = selector.xpath('//tbody[@id="J_HoverShow"]//td')
					for info in infos:
						info = utils.clean(utils.list_to_str(info.xpath('.//text()')))
						if '保证金' in info:
							item.margin = utils.get_money(info)
						if '程序' in info:
							item.phase = utils.get_phase(info)
						if '评估价' in info or '市场价' in info:
							item.appraisal_price = utils.get_money(info)
						if '起拍价' in info or '变卖价' in info or '起始价' in info:
							item.starting_price = utils.get_money(info)
						if not item.current_price and '变卖预缴款' in info:
							item.current_price = utils.get_money(info)
						if '竞价周期' in info or '变卖周期' in info:
							item.bidding_period = info.replace('竞价周期:','')
						if '延时周期' in info:
							item.delay_period = info.replace('延时周期:','')
						if '优先购买权人' in info:
							item.privileged_people = info.replace('优先购买权人:','')
						if '加价幅度' in info:
							item.markup = utils.get_money(info)
					
					url1 = utils.outFirst(selector.xpath('//div[@id="J_desc"]/@data-from'))
					if isinstance(url1, str):
						if 'http' not in url1:
							url1 = 'https:' + url1
						response = self.session.get(url1)
						text = utils.clean(utils.list_to_str(utils.clean_tags(response.text)))
						if '\\u' in text:
							text = text.encode('utf-8').decode('unicode_escape')
						item.intro += text

					url2 = utils.outFirst(selector.xpath('//div[@id="J_NoticeDetail"]/@data-from'))
					if isinstance(url2, str):
						if 'http' not in url2:
							url2 = 'https:' + url2
						response = self.session.get(url2)
						text = utils.clean(utils.list_to_str(utils.clean_tags(response.text)))
						if '\\u' in text:
							text = text.encode('utf-8').decode('unicode_escape')
						item.intro += text

					url3 = utils.outFirst(selector.xpath('//div[@id="J_ItemNotice"]/@data-from'))
					if isinstance(url3, str):
						if 'http' not in url3:
							url3 = 'https:' + url3
						response = self.session.get(url3)
						text = utils.clean(utils.list_to_str(utils.clean_tags(response.text)))
						if '\\u' in text:
							text = text.encode('utf-8').decode('unicode_escape')
						item.intro += text

					try:
						attache_params = {
							'callback': 'json',
							'id': item.repeat
						}
						response = self.session.get('https://sf-item.taobao.com/json/get_gov_attach.htm', params=attache_params)
						attaches = demjson.decode(utils.escape_jsonp(response.text, 'list'))
						item.attaches = str([{'name': attache['title'], 'url': 'https://sf.taobao.com/download_attach.do?attach_id=RNQFK74OBJNIG' + attache['id']} for attache in attaches])
					except Exception as e:
						logger.info(SITE_ID,'请求附件信息',e,item.url)

					if isinstance(item.people_bid, int) and item.people_bid > 0 and item.status in ['2','3','4','5']:
						try:
							bids_params = {
								'currentPage': '1',
								'callback': 'json',
								'records_type': 'pageRecords',
								'id': item.repeat
							}
							response = self.session.get('https://susong-item.taobao.com/json/get_bid_records.htm', params=bids_params)
							bids = demjson.decode(utils.escape_jsonp(response.text, 'dict'))
							item.bids = bids
						except Exception as e:
							logger.info(SITE_ID,'新建时请求竞价记录',e,item.url)

						try:
							confirm_params = {
								'callback': 'json',
								'itemId': item.repeat
							}
							response = self.session.get('https://sf.taobao.com/json/getSfDealConfirm.do', params=confirm_params)
							confirm = demjson.decode(utils.escape_jsonp(response.text, 'dict'))
							item.purchaser = confirm
						except Exception as e:
							logger.info(SITE_ID,'新建时请求竞价确认书',e,item.url)

					if url1 == None and url2 == None and url3 == None:
						# 判定当前页面请求失败
						self.err_times = 0
						time.sleep(SLEEP_SECONDS)
						return -1, item
					else:
						# 判定详情页请求成功,cookie及类的错误次数归零
						self.cookie_obj['err_times'] = 0
						self.err_times = 0
						return 1, item
				else:
					self.err_times += 1
					return self.parse_detail(item)
			except Exception as e:
				logger.info(SITE_ID,'获取详情页',e,item.url)
				self.err_times += 1
				return self.parse_detail(item)
		else:
			logger.error(SITE_ID,'放弃获取详情',None,item.url)
			self.err_times = 0
			return 0, item

	def update_item(self, item:db.Item):
		if self.err_times <= 2:
			try:
				response = self.session.get(url=item.url)
				if response.status_code == 200:
					selector = etree.HTML(response.text)
					item.status = '2'
					item.current_price = utils.get_money(utils.outFirst(selector.xpath('//span[contains(@class,"current-price")]/em/text()')))
					item.deal_time = utils.formate_timestamp(utils.outFirst(selector.xpath('//span[contains(@class,"J_TimeLeft")]/text()')))
					item.deal_price = utils.get_money(utils.outFirst(selector.xpath('//span[contains(@class,"current-price")]/em/text()')))
					item.people_signed = utils.get_int(utils.outFirst(selector.xpath('//div[@class="pm-remind"]/span[contains(@class,"pm-apply")]/em/text()')))
					item.people_alarmed = utils.get_int(utils.outFirst(selector.xpath('//div[@class="pm-remind"]/span[contains(@class,"pm-reminder")]/em/text()')))
					item.people_bid = utils.get_int(utils.outFirst(selector.xpath('//span[@class="J_Record"]/text()')))
					item.people_viewed = utils.get_int(utils.outFirst(selector.xpath('//div[@class="pm-remind"]/span[contains(@class,"pm-surround")]/em/text()')))

					if isinstance(item.people_bid, int) and item.people_bid > 0 and item.status in ['2','3','4','5']:
						try:
							bids_params = {
								'currentPage': '1',
								'callback': 'json',
								'records_type': 'pageRecords',
								'id': item.repeat
							}
							response = self.session.get('https://susong-item.taobao.com/json/get_bid_records.htm', params=bids_params)
							bids = demjson.decode(utils.escape_jsonp(response.text, 'dict'))
							item.bids = bids
						except Exception as e:
							logger.info(SITE_ID,'更新时请求竞价记录',e,item.url)

						try:
							confirm_params = {
								'callback': 'json',
								'itemId': item.repeat
							}
							response = self.session.get('https://sf.taobao.com/json/getSfDealConfirm.do', params=confirm_params)
							confirm = demjson.decode(utils.escape_jsonp(response.text, 'dict'))
							item.purchaser = confirm
						except Exception as e:
							logger.info(SITE_ID,'更新时请求竞价确认书',e,item.url)

					if item.people_signed == None and item.people_signed == None and item.people_signed and item.people_signed == None:
						# 判定当前页面请求失败
						self.err_times = 0
						time.sleep(SLEEP_SECONDS)
						return -1, item
					else:
						# 判定详情页请求成功,cookie及类的错误次数归零
						self.cookie_obj['err_times'] = 0
						self.err_times = 0
						return 1, item
				else:
					self.err_times += 1
					return self.update_item(item)
			except Exception as e:
				logger.info(SITE_ID,'更新详情页',e,item.url)
				self.err_times += 1
				return self.update_item(item)
		else:
			logger.error(SITE_ID,'放弃更新详情页',None,item.url)
			self.err_times = 0
			return 0, item

	def expand_items(self, items:list):
		while len(items) > 0:
			item = items.pop()
			if len(self.useful_cookies) <= 1:
				self.err_times = 0
				self.correct_count = 0
				self.session.close()
				update_all_cookies()
				self.useful_cookies = db.get_cookies(SITE_ID,True)
				self.cookie_obj = random.choice(self.useful_cookies)
				self.cookie = utils.format_sele_cookies(self.cookie_obj['cookie'].cookie)
				self.session = utils.get_session(utils.process_headers(consts.sf_pc_detail_headers))

			if self.cookie_obj['err_times'] >= DISABLE_ACCOUNT_LEVEL:
				self.useful_cookies.remove(self.cookie_obj)
				db.disable_cookie(self.cookie_obj)
				self.cookie_obj = random.choice(self.useful_cookies)
				self.cookie = utils.format_sele_cookies(self.cookie_obj['cookie'].cookie)
				self.session.close()
				self.session = utils.get_session(utils.process_headers(consts.sf_pc_detail_headers), self.cookie)

			if self.correct_count >= CHANGE_ACCOUNT_LEVEL:
				self.correct_count = 0
				self.cookie_obj = random.choice(self.useful_cookies)
				self.cookie = utils.format_sele_cookies(self.cookie_obj['cookie'].cookie)
				self.session.close()
				self.session = utils.get_session(utils.process_headers(consts.sf_pc_detail_headers), self.cookie)
			
			if self.err_times <= 4:
				status_code, item = self.parse_detail(item)
				if status_code == 1:
					self.correct_count += 1
					yield item
				elif status_code == 0:
					self.correct_count = 0
					continue
				elif status_code == -1:
					self.cookie_obj['err_times'] += 1
					self.correct_count = 0
					self.cookie_obj = random.choice(self.useful_cookies)
					self.cookie = utils.format_sele_cookies(self.cookie_obj['cookie'].cookie)
					self.session.close()
					self.session = utils.get_session(utils.process_headers(consts.sf_pc_detail_headers), self.cookie)
					items.append(item)
					continue
				else:
					logger.error(SITE_ID,'新建时判断status_code',None,status_code)
					continue
			else:
				self.err_times = 0
				self.correct_count = 0
				logger.error(SITE_ID,'新建时放弃ali-sf的详情页',None,item.url)
				continue

	def update_items(self, items:list):
		while len(items) > 0:
			item = items.pop()
			if len(self.useful_cookies) <= 1:
				self.err_times = 0
				self.correct_count = 0
				self.session.close()
				update_all_cookies()
				self.useful_cookies = db.get_cookies(SITE_ID,True)
				self.cookie_obj = random.choice(self.useful_cookies)
				self.cookie = utils.format_sele_cookies(self.cookie_obj['cookie'].cookie)
				self.session = utils.get_session(utils.process_headers(consts.sf_pc_detail_headers))

			if self.cookie_obj['err_times'] >= DISABLE_ACCOUNT_LEVEL:
				self.useful_cookies.remove(self.cookie_obj)
				db.disable_cookie(self.cookie_obj)
				self.cookie_obj = random.choice(self.useful_cookies)
				self.cookie = utils.format_sele_cookies(self.cookie_obj['cookie'].cookie)
				self.session.close()
				self.session = utils.get_session(utils.process_headers(consts.sf_pc_detail_headers))

			if self.correct_count >= CHANGE_ACCOUNT_LEVEL:
				self.correct_count = 0
				self.cookie_obj = random.choice(self.useful_cookies)
				self.cookie = utils.format_sele_cookies(self.cookie_obj['cookie'].cookie, '.taobao.com')
				self.session.close()
				self.session = utils.get_session(utils.process_headers(consts.sf_pc_detail_headers), self.cookie)
			
			if self.err_times <= 4:
				status_code, item = self.update_item(item)
				if status_code == 1:
					self.correct_count += 1
					yield item
				elif status_code == 0:
					self.correct_count = 0
					continue
				elif status_code == -1:
					self.cookie_obj['err_times'] += 1
					self.correct_count = 0
					self.cookie_obj = random.choice(self.useful_cookies)
					self.cookie = utils.format_sele_cookies(self.cookie_obj['cookie'].cookie)
					self.session.close()
					self.session = utils.get_session(utils.process_headers(consts.sf_pc_detail_headers), self.cookie)
					items.append(item)
					continue
				else:
					logger.error(SITE_ID,'更新时判断status_code',None,status_code)
					continue

			else:
				self.err_times = 0
				self.correct_count = 0
				logger.info(SITE_ID,'更新时放弃ali-sf的详情页',None,item.url)
				continue

class Ali_sf(object):
	def __init__(self):
		pass

	def _run_(self):
		# 新项目的爬取
		parser = Parse_detail()
		for province in consts.sf_province:
			# os.system('taskkill /F /im chromedriver.exe')
			# os.system('taskkill /F /im chrome.exe')
			repeat_set = db.get_items_repeat(1, province[1])
			get_urls = Get_urls(repeat_set)
			for category in consts.sf_category:
				for page in range(1,category[1]+1): # 爬取每个种类指定页数的内容
					driver = get_urls.access_page(province, category, page)
					items = get_urls.parse_urls(province, category, driver)
					for item in parser.expand_items(items):
						item = process_item(item)
						upload_item(item)
						time.sleep(2)

		# 已爬取项目的更新
		update_items = db.get_update_items()
		for item in parser.update_items(update_items):
			item = process_updated_item(item)
			upload_updated_item(item)
