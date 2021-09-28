import json
import random
import requests
import datetime
from utils import utils
import alchemy as db
from utils.consts import industry_a,industry_b,industry_c
from data_formate import Item,Bid,Purchaser

BAIDU_KEY = 'fQRhL0wpemGpGGKIkUMUhGqXfe96wOmM'
USER_AGENTS = [
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR"
    " 2.0.50727; ""Media Center PC 6.0)","Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; "
    "SLCC2; .NET CLR 2.0.50727; .NET ""CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; "
    "InfoPath.2; .NET CLR3.0.04506.30)","Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15"
    " (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5"
]

def formate_bids(item:Item):
    """
    整理item.bids的数据格式
    """
    results = []
    if isinstance(item.bids, dict) and isinstance(item.bids.get('records'), list):
        bids = item.bids.get('records')
        for bid in bids:
            new_bid = Bid()
            new_bid.code = bid.get('alias')
            new_bid.price = utils.get_money(bid.get('price'))
            new_bid.bid_time = utils.formate_timestamp(bid.get('date'))
            results.append(new_bid)
    return results

def formate_purchaser(item:Item):
    result = Purchaser()
    if isinstance(item.purchaser, dict) and isinstance(item.purchaser.get('purchaseConfirm'), dict):
        confirm = item.purchaser.get('purchaseConfirm')
        result.name = confirm.get('buyerName')
        result.code = confirm.get('buyerAliasName')
        result.deal_time = utils.getNotNone(confirm.get('lastTime'), confirm.get('auctionEndTime'))
        result.price = confirm.get('priceCent')
        result.title = confirm.get('auctionTitle')
    return result

def get_code(item:Item):
    if not isinstance(item.updated_time, datetime.datetime):
        item.updated_time = datetime.datetime.now()   
    return datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S')

def get_discount(item:Item):
    """
    计算折扣率,作为item.discount
    """
    sell_price = utils.get_num(item.starting_price, item.current_price, item.max_price, item.deal_price, item.appraisal_price)
    base_price = utils.get_num(item.appraisal_price, item.deal_price, item.max_price, item.current_price, item.starting_price)
    if isinstance(sell_price, (int, float)) and isinstance(base_price, (int, float)):
        result = round(100 * sell_price / base_price,2)
        if result > 100 or result < 0:
            result = 100
        return result
    else:
        return 100

def get_updated_discount(item:db.Item):
    """
    计算更新后的折扣率
    """
    sell_price = utils.get_num(item.deal_price, item.max_price, item.current_price, item.starting_price, item.appraisal_price)
    base_price = utils.get_num(item.appraisal_price, item.starting_price, item.current_price, item.max_price, item.deal_price)
    if isinstance(sell_price, (int, float)) and isinstance(base_price, (int, float)):
        result = round(100 * sell_price / base_price,2)
        if result < 0:
            result = 0
        return result
    else:
        return 100

def get_school(item:Item):
    """
    获取教育学校字段
    """
    return '教育学校全面信息详见电脑版网站地图地理信息'

def get_envir(item:Item):
    """
    股权债权类获取行业,房地产类提供默认字段值
    """
    if item.categoryId in []:
        if item.industryId_c:
            return industry_c[item.industryId_c - 1]
        elif item.industryId_b:
            return industry_b[item.industryId_b - 1]
        elif item.industryId_a:
            return industry_a[item.industryId_a - 1]
        else:
            return '其他'
    else:
        return '环境配套超市医院健身娱乐银行等全面信息详见电脑版网站地图地理信息'

def get_contactor(item:Item):
    return '资产信息网'

def get_traffic(item:Item):
    return '交通全面信息详见电脑版网站地图地理信息'

def get_contact_phone(item:Item):
    return '021-68828928'

def get_coordinate(item:Item):
    """
    请求百度api获取Item项目经纬度
    """
    if item.location:
        location = item.location
    elif item.title:
        location = item.title
    else:
        return None, None

    try:
        params = {
            'address': location,
            'ak': BAIDU_KEY,
            'output': 'json',
        }
        response = requests.get('http://api.map.baidu.com/geocoding/v3/', params=params)
        datas = json.loads(response.text)
        if datas['status'] == 0:
            # 4.1-请求和返回都成功，则进行解析
            tmpList = datas['result']['location']  # 获取所有结果坐标点
            lng = round(tmpList['lng'], 6)
            lat = round(tmpList['lat'], 6)
            return lng, lat
        else:
            # 4.3-如果发生其他错误则返回-2
            return None, None
    except Exception as e:
        print(f'请求百度api获取坐标时错误:{e}')
        return None, None

def getAccessToken():
    """
    获取使用贝壳房屋价值报告api的token
    """
    url = 'https://gw-open.ke.com/oauth/token'
    headers = {
        'user-agent': '"Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",',
        'Accept-Encoding':'gzip, deflate',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'gw-open.ke.com',
            }
    data = {
        'grant_type':'client_credentials',
        'client_id':'1fe6c97a468f4c4fbafac667ecd96456',
        'client_secret':'7a210e70c3fa4e10b46db5813b16d55f'
    }
    response = requests.post(url,headers=headers,data=data)
    access_token = json.loads(response.text).get('data').get('access_token')
    return access_token

TOKEN = getAccessToken()

def getAppraised(addr, area):
    """
    请求贝壳api并返回内容
    """
    url = 'https://gw-open.ke.com/api/assessPriceReportPrejudge'
    headers = {
        'user-agent': random.choice(USER_AGENTS),
        'Content-Type':'application/x-www-form-urlencoded',
        'access_token': TOKEN
    }
    data = {
        'standPriceAssessBuildArea': area,
        'standDetailedAddress': addr
    }
    response = requests.post(url,headers=headers,data=data)
    return json.loads(response.text)

def get_report(item:Item):
    """
    请求贝壳api判断项目是否可获取价值报告
    """
    try:
        area = item.area
        if not area:
            area = 100
        if not item.location:
            return False
        response = getAppraised(item.location, area)
        if response.get('data'):
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False
