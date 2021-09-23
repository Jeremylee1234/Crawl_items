import re
import time
import json
import datetime
import requests
from item import Item
from retrying import retry
from lxml.etree import _Element
from utils.config import global_config
from utils.logger import logger

## 各种内容处理函数

def get_id():
    """
    根据当前时间创建项目id(js整数格式时间戳)
    """
    now = datetime.datetime.now()
    date_benchmark = datetime.datetime(2000,1,1,0,0,0,0)
    timedelta = now - date_benchmark
    return int(timedelta.total_seconds()*10000)

def get_money(string, unit=1):
    """
    对价格进行进一步修正:
    字符串:尝试提取其中的价格
    数值:直接返回该值
    """
    if isinstance(string,str):
        if '百万' in string:
            pattern = re.compile(r'[\d,.]+')
            numbers = re.findall(pattern,string)
            if len(numbers) >= 1:
                for number in numbers:
                    try:
                        return float(number[0].replace(',','')) * 1000000 * unit
                    except:
                        continue
            else:
                return None
        elif '万' in string:
            pattern = re.compile(r'[\d,.]+')
            numbers = re.findall(pattern,string)
            if len(numbers) >= 1:
                for number in numbers:
                    try:
                        return float(number[0].replace(',','')) * 10000 * unit
                    except:
                        continue
            else:
                return None
        else:
            pattern = re.compile(r'[\d,.]+')
            numbers = re.findall(pattern,string)
            if len(numbers) >= 1:
                for number in numbers:
                    try:
                        return float(number[0].replace(',','')) * unit
                    except:
                        continue
            else:
                return None
    elif isinstance(string,float):
        return string
    elif isinstance(string,int):
        return float(string) * unit
    else:
        return None

def get_session(headers=None, cookies=None):
    """
    创建requests.session
    headers:当需要header时传入heders,否则设置为默认的通用headers
    cookies:当需要cookie时传入cookie
    """
    session = requests.session()
    if not headers:
        session.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Connection': 'keep-alive'
        }
    else:
        session.headers = headers
    if cookies:
        session.cookies = cookies
    return session

def getNotNone(*strs):
    """
    获取全部传入的变量中首个非空的变量的值
    strs:全部传入变量
    """
    for r in strs:
        if r:
            return r
        else:
            continue

def get_num(*args):
    """
    获取全部传入的变量中首个非0的数值型变量值
    strs:全部传入变量
    """
    for arg in args:
        if isinstance(arg, (float, int)):
            if arg == 0:
                continue
            else:
                return arg
        else:
            continue
    return 0

def clean_tags(string:str):
    """
    对html格式的文本清洗只取其纯文本内容,列表形式返回值
    string:文本内容
    """
    if '<' in string:
        patt = re.compile(r'>(.*?)<')
        return re.findall(patt, string)
    else:
        return [string]

def clean(string:str):
    """
    简单清洗文本,去除其中的部分特殊字符
    """
    if isinstance(string, str):
        bad_str = [' ','    ','\r','\n','\t','\\','\\r','\\n','\\t','&nbsp;']
        for b in bad_str:
            string = string.replace(b, '')
        return ''.join(string.split())
    else:
        return string

def outFirst(contents, type=1):
    """
    处理lxml通过xpath选取到的元素列表,返回所需要的内容
    contents:元素列表
    type:通过其值指定所需要返回的类型
    type=1:默认值,返回列表中首个字符串
    type=2:返回列表中首个元素对象
    type为其他:现与type=1相同,后续根据需要拓展
    """
    if isinstance(contents, list):
        if contents == []:
            return None
        elif len(contents) >= 1:
            if type == 1:
                obj_type = str
            elif type == 2:
                obj_type = _Element
            else:
                obj_type = str
            for content in contents:
                if isinstance(content, obj_type):
                    return content
                else:
                    continue
        else:
            return None

def list_to_str(contents:list):
    """
    将文本列表转为字符串
    contents:文本列表
    """
    num_head_patt = re.compile(r'^[\d\.].*?$')
    num_foot_patt = re.compile(r'^.*?[\d\.]$')
    result = ''
    if isinstance(contents, list):
        strings = []
        for content in contents:
            if isinstance(content, str) and content != '':
                content = clean(content)
                strings.append(content)
        
        for index,string in enumerate(strings):
            result += string
            if re.match(num_foot_patt, string) and index != len(strings)-1 and re.match(num_head_patt, strings[index+1]):
                result += ';'

        return result
    elif isinstance(contents, str):
        return contents
    else:
        return result

## selenium操作函数

def isElementExist(driver, xpath):
    """
    判断selenium浏览器窗口中是否存在xpath所对应的元素
    """
    try:
        element = driver.find_elements_by_xpath(xpath)
        if len(element) >= 1:
            return True
        else:
            return False
    except:
        return False

def find_all_sele_xpath(driver, *xpaths):
    """
    尝试获取selenium浏览器句柄中多个xpath元素对象组成列表
    """
    results = []
    for xpath in xpaths:
        try:
            elements = driver.find_elements_by_xpath(xpath)
            for element in elements:
                results.append(element)
        except Exception as e:
            print(e)
            continue
    return results

## 处理cookies

def format_cookies(cookie):
    """
    将字符串格式cookie解析为session格式cookie
    """
    manual_cookies = {}
    for item in cookie.split(';'):
        name, value = item.strip().split('=', 1)
        # 用=号分割，分割1次
        manual_cookies[name] = value
        # 为字典cookies添加内容
    cookiesJar = requests.utils.cookiejar_from_dict(manual_cookies, cookiejar=None, overwrite=True)
    return cookiesJar

def format_sele_cookies(sele_cookie,):
    """
    将selenium格式cookie解析为session格式cookie
    """
    manual_cookies = {}
    cookies = json.loads(sele_cookie)
    for cookie in cookies:
        try:
            name = cookie.get('name')
            value = cookie.get('value')
            if name and value:
                manual_cookies[name] = value
            else:
                continue
        except Exception as e:
            logger.ingo(f'尝试解析selenium的cookie时出错:{e}')
            continue
    cookiesJar = requests.utils.cookiejar_from_dict(manual_cookies, cookiejar=None, overwrite=True)
    return cookiesJar

## 规范化Item属性值
def get_phase(string:str):
    """
    获取拍卖阶段
    """
    if isinstance(string, str):
        if '一' in string:
            return '一拍'
        elif '二' in string:
            return '二拍'
        elif '卖' in string:
            return '变卖'
        elif string != '':
            return '重新拍卖'
        else:
            return '其他'
    else:
        return '其他'

def parse_coordinate(string:str):
    if isinstance(string, str):
        try:
            results = string.split(',')
            if len(results) >= 2:
                return float(results[0]), float(results[1])
            else:
                return None, None
        except Exception as e:
            logger.error(f'处理经纬度时出错:{e}')
    else:
        return None, None

def formate_timestamp(time_num):
    try:
        if isinstance(time_num, int):
            time_begin = datetime.datetime(1970,1,1,8,0,0)
            time = time_begin + datetime.timedelta(milliseconds=time_num)
            return time
        elif isinstance(time_num, str):
            if re.match(r'^\d*$', time_num):
                time_begin = datetime.datetime(1970,1,1,8,0,0)
                time = time_begin + datetime.timedelta(milliseconds=int(time_num))
                return time
            elif re.match(r'\d{4}年\d{1,2}月\d{1,2}', time_num):
                time_num = re.findall(r'\d{4}年\d{1,2}月\d{1,2}', time_num)[0]
                return datetime.datetime.strptime(time_num, '%Y年%m月%d')
            elif re.match(r'\d{4}-\d{1,2}-\d{1,2}', time_num):
                time_num = re.findall(r'\d{4}-\d{1,2}-\d{1,2}', time_num)[0]
                return datetime.datetime.strptime(time_num, '%Y-%m-%d')
            else:
                logger.info(f'日期{time_num}的格式无法识别')
                return None
        else:
            return None
    except Exception as e:
        logger.error(f'日期{time_num}处理时出错:{e}')
        return None

## 二次解析item内容

# Bug
def sort_item(item:Item):
    """
    通过字符匹配二次判断部分需要重新判断category的项目
    item:Item对象,其中存储项目信息
    """
    if isinstance(item.get('title'),str) and item.get('category_id') in [21,99,25,15,14,13,12,4,None]:
        if '股' in item['title'] or '债权' in item['title']:
            item['category'] = '股权债权'
            item['category_id'] = 12
        elif '增资' in item['title'] or '混改' in item['title'] or '扩股' in item['title']:
            item['category'] = '项目投融资'
            item['category_id'] = 14
        elif '土地' in item['title'] or '用地' in item['title']:
            item['category'] = '土地'
            item['category_id'] = 9
        elif '工程' in item['title']:
            item['category'] = '项目和工程'
            item['category_id'] = 15
        elif '无形' in item['title'] or '商标' in item['title'] or '专利' in item['title'] or '营运' in item['title'] or '著作' in item['title']:
            item['category'] = '无形资产'
            item['category_id'] = 25
        elif '酒店' in item['title']:
            item['category'] = '酒店'
            item['category_id'] = 4
        elif '林' in item['title'] or '矿' in item['title']:
            item['category'] = '林地矿地'
            item['category_id'] = 11
        elif '物流' in item['title'] or '仓库' in item['title'] or '仓储' in item['title']:
            item['category'] = '物流'
            item['category_id'] = 6
        elif '办公' in item['title'] or '大厦' in item['title'] or '写字楼' in item['title']:
            item['category'] = '办公'
            item['category_id'] = 21
        elif '厂房' in item['title'] or '车间' in item['title'] or '工业' in item['title']:
            item['category'] = '工业'
            item['category_id'] = 5
        elif '医' in item['title']:
            item['category'] = '医养'
            item['category_id'] = 7
        elif '旅游' in item['title']:
            item['category'] = '旅游地产'
            item['category_id'] = 8
        elif '租' in item['title']:
            item['category'] = '租赁权'
            item['category_id'] = 13
        elif '商铺' in item['title'] or '商业' in item['title'] or '门面' in item['title'] or '商住楼' in item['title']:
            item['category'] = '商业'
            item['category_id'] = 2
        elif '室' in item['title'] or '住宅' in item['title'] or '小区' in item['title'] or '房' in item['title'] or '户' in item['title']:
            item['category'] = '住宅'
            item['category_id'] = 1
        elif not isinstance(item.get('category_id'),int):
            item['category'] = '其他'
            item['category_id'] = 21
        else:
            pass
    else:
        pass
    
    return item

# Bug
def parse_datetimes(item:Item):
    """
    通过正则二次解析获取项目起始日期和结束日期
    """
    if item.get('start_date') and item.get('end_date'):
        return item
    else:
        period_patt = re.compile(r'\d{0,4}[年-]\d{1,2}[月-]\d{1,2}[日-]{0,1}.{0,10}[—起至到-].{0,10}\d{0,4}[年-]\d{1,2}[月-]\d{1,2}[日-]{0,1}')
        year_patt1 = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
        year_patt2 = re.compile(r'\d{4}-\d{1,2}-\d{1,2}')
        month_patt1 = re.compile(r'\d{1,2}月\d{1,2}日')
        
        year = datetime.datetime.now().year
        intro = item.get('intro')
        if not isinstance(intro, str):
            intro = str(intro)
            
        groups = re.findall(period_patt, intro)
        if len(groups) >= 1:
            period_data = groups[0]
        year_date = re.findall(year_patt1, period_data)
        year_date2 = re.findall(year_patt2, period_data)
        month_date = re.findall(month_patt1, period_data)
        if len(year_date) >= 2:
            start_date = datetime.datetime.strptime(year_date[0], '%Y年%m月%d日')
            end_date = datetime.datetime.strptime(year_date[1], '%Y年%m月%d日')
            item['start_date'] = datetime.datetime.strftime(start_date, '%Y-%m-%d')
            item['end_date'] = datetime.datetime.strftime(end_date, '%Y-%m-%d')
            return item
        elif len(year_date2) >= 2:
            start_date = datetime.datetime.strptime(year_date2[0], '%Y-%m-%d')
            end_date = datetime.datetime.strptime(year_date2[1], '%Y-%m-%d')
            item['start_date'] = datetime.datetime.strftime(start_date, '%Y-%m-%d')
            item['end_date'] = datetime.datetime.strftime(end_date, '%Y-%m-%d')
            return item
        elif len(year_date) == 1 and len(month_date) >= 2:
            start_date = datetime.datetime.strptime(year_date[0], '%Y年%m月%d日')
            end_date = datetime.datetime.strptime(month_date[1], '%m月%d日')
            end_date = end_date.replace(year = start_date.year)
            item['start_date'] = datetime.datetime.strftime(start_date, '%Y-%m-%d')
            item['end_date'] = datetime.datetime.strftime(end_date, '%Y-%m-%d')
            return item
        elif len(year_date) == 1:
            start_date = datetime.datetime.strptime(year_date[0], '%Y年%m月%d日')
            item['start_date'] = datetime.datetime.strftime(start_date, '%Y-%m-%d')
        elif len(year_date2) == 1:
            start_date = datetime.datetime.strptime(year_date2[0], '%Y-%m-%d')
            item['start_date'] = datetime.datetime.strftime(start_date, '%Y-%m-%d')
        elif len(month_date) >= 2:
            start_date = datetime.datetime.strptime(month_date[0], '%m月%d日')
            end_date = datetime.datetime.strptime(month_date[1], '%m月%d日')
            start_date = start_date.replace(year = year)
            end_date = end_date.replace(year = year)
            item['start_date'] = datetime.datetime.strftime(start_date, '%Y-%m-%d')
            item['end_date'] = datetime.datetime.strftime(end_date, '%Y-%m-%d')
            return item
        else:
            print('????? date period')
            print(period_data)
            pass

        if item.get('start_date') or item.get('end_date'):
            return item

        year_patt1_data = re.findall(year_patt1, intro)
        if len(year_patt1_data) >= 2:
            start_date = datetime.datetime.strptime(year_patt1_data[0], '%Y年%m月%d日')
            end_date = datetime.datetime.strptime(year_patt1_data[1], '%Y年%m月%d日')
            item['start_date'] = datetime.datetime.strftime(start_date, '%Y-%m-%d')
            item['end_date'] = datetime.datetime.strftime(end_date, '%Y-%m-%d')
            return item
        
        year_patt2_data = re.findall(year_patt2, intro)
        if len(year_patt2_data) >= 2:
            start_date = datetime.datetime.strptime(year_patt2_data[0], '%Y-%m-%d')
            end_date = datetime.datetime.strptime(year_patt2_data[1], '%Y-%m-%d')
            item['start_date'] = datetime.datetime.strftime(start_date, '%Y-%m-%d')
            item['end_date'] = datetime.datetime.strftime(end_date, '%Y-%m-%d')
            return item
        
        now = datetime.datetime.now()
        item['start_date'] = now + datetime.timedelta(days=15)
        item['end_date'] = now + datetime.timedelta(days=18)
        return item

# Bug
def get_position_infos(item:Item, all_province:list, all_city:list, all_county:list):
    """
    通过字符匹配尝试二次解析未获取到一二三级地址信息的项目的地址
    """
    datas = [item.get('province'), item.get('location'), item.get('title'), item.get('city'), item.get('intro')]
    province_flag = False
    province_obj = None
    city_flag = False
    city_obj = None
    county_flag = False
    county_obj = None
    
    for data in datas:
        if data is not None:
            if not province_flag:
                for province in all_province:
                    if province.province in data:
                        item['province'] = province.province
                        item['province_id'] = province.id
                        province_flag = True
                        province_obj = province
                        all_city = [city for city in all_city if city.parent_province == province.id]
                        all_county = [county for county in all_county if county.parent_city in [city.id for city in all_city]]
                        break
                    else:
                        continue
                    
                for city in all_city:
                    if city.city in data:
                        item['city'] = city.city
                        item['city_id'] = city.id
                        city_flag = True
                        city_obj = city
                        all_county = [county for county in all_county if county.parent_city == city.id]
                        if not province_flag:
                            for province in all_province:
                                if province.id == city.parent_province:
                                    item['province'] = province.province
                                    item['province_id'] = province.id
                                    province_flag = True
                                    province_obj = province
                                    break
                                else:
                                    continue
                        break
                    else:
                        continue
                
                for county in all_county:
                    if county.county in data:
                        item['county'] = county.county
                        item['county_id'] = county.id
                        county_flag = True
                        county_obj = county
                        if not city_flag:
                            for city in all_city:
                                if city.id == county.parent_city:
                                    item['city'] = city.city
                                    item['city_id'] = city.id
                                    city_flag = True
                                    city_obj = city
                                    if not province_flag:
                                        for province in all_province:
                                            if province.id == city.parent_province:
                                                item['province'] = province.province
                                                item['province_id'] = province.id
                                                province_flag = True
                                                province_obj = province
                                                break
                                            else:
                                                continue
                                    break
                                else:
                                    continue
                        break
                    else:
                        continue


            elif not city_flag:
                for city in all_city:
                    if city.city in data:
                        item['city'] = city.city
                        item['city_id'] = city.id
                        city_flag = True
                        city_obj = city
                        all_county = [county for county in all_county if county.parent_city == city.id]
                        break
                    else:
                        continue
                
                for county in all_county:
                    if county.county in data:
                        item['county'] = county.county
                        item['county_id'] = county.id
                        county_flag = True
                        county_obj = county
                        if not city_flag:
                            for city in all_city:
                                if city.id == county.parent_city:
                                    item['city'] = city.city
                                    item['city_id'] = city.id
                                    city_flag = True
                                    city_obj = city
                                    break
                                else:
                                    continue
                        break
                    else:
                        continue
            elif not county_flag:
                for county in all_county:
                    if county.county in data:
                        item['county'] = county.county
                        item['county_id'] = county.id
                        county_flag = True
                        county_obj = county
                        break
                    else:
                        continue
            else:
                if not county_obj.parent_city == city_obj.id:
                    for city in all_city:
                        if city.id == county.parent_city:
                            item['city'] = city.city
                            item['city_id'] = city.id
                            city_flag = True
                            city_obj = city
                            break
                        else:
                            continue
                if not city_obj.parent_province == province_obj.id:
                    for province in all_province:
                        if province.id == city.parent_province:
                            item['province'] = province.province
                            item['province_id'] = province.id
                            province_flag = True
                            province_obj = province
                            break
                        else:
                            continue
                return item
        else:
            continue
    else:
        if city_flag:
            if not city_obj.parent_province == province_obj.id:
                for province in all_province:
                    if province.id == city.parent_province:
                        item['province'] = province.province
                        item['province_id'] = province.id
                        province_flag = True
                        province_obj = province
                        break
                    else:
                        continue
        return item

# Bug
def get_ratio(item:Item):
    """
    通过正则解析尝试获取股权债权类项目的转让比例
    """
    title_ratio_patt = re.compile(r'(\d+).*?%')
    intro_ratio_patt_a = re.compile(r'(转让|融资|扩股|募集|集资|收购|增资|投资方).{0,30}?([\d\.]{1,8}).{0,10}%.{0,15}?([\d\.]{0,10})')
    if item['category_id'] in [12,14,16,17,19,20,22,25]:
        if isinstance(item['title'], str):
            title_ratios = re.findall(title_ratio_patt, item['title'])
            if len(title_ratios) >= 1:
                item['extra5'] = title_ratios[0]
                return item
        if isinstance(item['intro'], str):
            intro_ratio_a = re.findall(intro_ratio_patt_a, item['intro'])
            for intro_ratio in intro_ratio_a:
                try:
                    number = float(intro_ratio[1])
                    if number <= 100:
                        item['extra5'] = number
                        return item
                    else:
                        continue
                except:
                    continue
            for intro_ratio in intro_ratio_a:
                try:
                    number = float(intro_ratio[2])
                    if number <= 100:
                        item['extra5'] = number
                        return item
                    else:
                        continue
                except:
                    continue
    return item

# Bug
def get_location(province, city, county):
    """
    对已确定三级地址信息但未获取到location字段的项目粗略设置location字段值
    """
    if county is None:
        if city is None:
            if province is None:
                return None
            else:
                return str(province)
        else:
            return str(province) + str(city)
    else:
        return str(province) + str(city) + str(county)

# Bug
def get_area(intro):
    """
    尝试从项目说明中获取面积字段值
    """
    try:
        if isinstance(intro, str):
            float_patt = re.compile(r'\d{1,7}\.\d{1,4}')
            pattern1 = re.compile(r'面积.{0,30}\d{1,7}\.\d{1,4}.{0,5}[平mM㎡]')
            groups1 = re.findall(pattern1, intro)
            pattern2 = re.compile(r'\d{1,7}\.\d{1,4}.{0,5}[平mM㎡]')
            groups2 = re.findall(pattern2, intro)
            pattern3 = re.compile(r'[\d\.]{2,12}.{0,5}亩')
            groups3 = re.findall(pattern3, intro)
            pattern4 = re.compile(r'面积.{0,100}\d{1,7}\.\d{1,4}')
            groups4 = re.findall(pattern4, intro)
            pattern5 = re.compile(r'面积.{0,10}\d{1,7}\.\d{1,4}')
            groups5 = re.findall(pattern5, intro)
            all_group = [groups1,groups2,groups3,groups4,groups5]

            for group in all_group:
                if len(group) >= 1:
                    obj = group[0].replace(',','').replace('，','')
                    results = re.findall(float_patt, obj)
                    for result in results:
                        try:
                            return float(result)
                        except:
                            continue

            num_patt = re.compile(r'[\d\.]{2,9}')
            pattern6 = re.compile(r'面积.{0,30}[\d\.]{2,9}.{0,5}[平mM㎡]')
            groups6 = re.findall(pattern6, intro)
            pattern7 = re.compile(r'[\d\.]{2,9}.{0,5}[平mM㎡]')
            groups7 = re.findall(pattern7, intro)
            pattern8 = re.compile(r'[\d\.]{2,9}.{0,5}亩')
            groups8 = re.findall(pattern8, intro)
            pattern9 = re.compile(r'面积.{0,100}[\d\.]{2,9}')
            groups9 = re.findall(pattern9, intro)
            pattern10 = re.compile(r'面积.{0,10}[\d\.]{2,9}')
            groups10 = re.findall(pattern10, intro)
            all_group = [groups6,groups7,groups8,groups9,groups10]

            for group in all_group:
                if len(group) >= 1:
                    obj = group[0].replace(',','').replace('，','')
                    results = re.findall(num_patt, obj)
                    for result in results:
                        try:
                            return float(result)
                        except:
                            continue
            
            return None

        else:
            return None
    except Exception as e:
        print(e)
        return None

def retry_on_result_none(result):
    """
    用于配合retry模块使用
    """
    return result is None

class Proxy(object):
    """
    请求ip代理
    """
    def __init__(self):
        self.err_times = 0
        self.max_retry = 20
    
    @retry(retry_on_result=retry_on_result_none)
    def get_proxy(self):
        """
        请求并解析代理ip
        """
        proxy_url = global_config.getRaw('config','proxy_url')
        if self.err_times <= self.max_retry:
            try:
                data = requests.get(proxy_url).json()
                ip = f'{data["data"][0]["ip"]}:{data["data"][0]["port"]}' # 更换服务商时修改
                proxy = { 'http': 'http://'+ip, 'https': 'http://'+ip }
                proxy_test = requests.get('https://www.baidu.com', proxies=proxy, timeout=10)

                if proxy_test.status_code ==200:
                    self.err_times = 0
                    print(ip, proxy)
                    return ip, proxy
                else:
                    print(proxy_test)
                    time.sleep(1)
                    self.err_times += 1
                    return None
            except Exception as e:
                print(e)
                time.sleep(3)
                self.err_times += 1
                return None
        else:
            print('max retry with get proxy and finally give up')
            self.err_times = 0
            time.sleep(60)
            return None

if __name__ == '__main__':
    proxy = Proxy()
    proxy.get_proxy()