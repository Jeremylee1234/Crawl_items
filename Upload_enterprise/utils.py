#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import consts
import re

def formate_data(item:dict):
  """
  将读取天眼查和企查查所获得的数据字典整理成统一格式的键值对,添加新的数据源时需要修改该函数
  item:传入的数据字典
  """
  if item['source'] == 'qcc':
    return {
      '公司名称': item.get('企业名称'),
      '经营状态': item.get('登记状态'),
      '法定代表人': item.get('法定代表人'),
      '注册资本': item.get('注册资本'),
      '实缴资本': None,
      '成立日期': item.get('成立日期'),
      '核准日期': item.get('核准日期'),
      '营业期限': None,
      'province': item.get('所属省份'),
      'city': item.get('所属城市'),
      'county': item.get('所属区县'),
      '统一社会信用代码': item.get('统一社会信用代码'),
      '纳税人识别号': item.get('纳税人识别号'),
      '注册号': item.get('注册号'),
      '组织机构代码': item.get('组织机构代码'),
      '参保人数': item.get('参保人数'),
      '企业类型': item.get('企业类型'),
      '所属行业': item.get('所属行业'),
      '曾用名': item.get('曾用名'),
      '英文名': item.get('英文名'),
      '注册地址': item.get('企业地址'),
      '最新地址': item.get('最新年报地址'),
      '网址': item.get('网址'),
      '联系电话': f'{item.get("电话")}；{item.get("更多电话")}',
      '联系邮箱': f'{item.get("邮箱")}；{item.get("更多邮箱")}',
      '经营范围': item.get('经营范围')
    }
  elif item['source'] == 'tyc':
    return {
      '公司名称': item.get('公司名称'),
      '经营状态': item.get('经营状态'),
      '法定代表人': item.get('法定代表人'),
      '注册资本': item.get('注册资本'),
      '实缴资本': item.get('实缴资本'),
      '成立日期': item.get('成立日期'),
      '核准日期': item.get('核准日期'),
      '营业期限': item.get('营业期限'),
      'province': item.get('所属省份'),
      'city': item.get('所属城市'),
      'county': item.get('所属区县'),
      '统一社会信用代码': item.get('统一社会信用代码'),
      '纳税人识别号': item.get('纳税人识别号'),
      '注册号': item.get('注册号'),
      '组织机构代码': item.get('组织机构代码'),
      '参保人数': item.get('参保人数'),
      '企业类型': item.get('公司类型'),
      '所属行业': item.get('所属行业'),
      '曾用名': item.get('曾用名'),
      '英文名': None,
      '注册地址': item.get('注册地址'),
      '最新地址': item.get('最新年报地址'),
      '网址': item.get('网址'),
      '联系电话': f'{item.get("电话")};{item.get("其他电话")}',
      '联系邮箱': f'{item.get("邮箱")};{item.get("其他邮箱")}',
      '经营范围': item.get('经营范围')
    }
  else:
    return {}

def get_str(string:str):
  if isinstance(string,str) and string != '-':
    return string.strip()
  else:
    return ''
  
def get_int(string:str):
  if isinstance(string,str):
    pattern = re.compile(r'\d+')
    num = re.search(pattern, string).group()
    return int(num)
  else:
    return 0

def get_status(string:str):
  if isinstance(string,str):
    if '在业' or '存续' in string:
      return 1
    elif '清算' in string:
      return 2
    elif '吊销' in string:
      return 3
    elif '注销' in string:
      return 4
    elif '停业' in string:
      return 5
    elif '撤销' in string:
      return 6
    elif '迁入' in string:
      return 7
    elif '迁出' in string:
      return 8
    else:
      print(string)
      return 1
  else:
    return 1

def get_money(string:str):
  if isinstance(string,str):
    try:
      pattern = re.compile(r'\d+(\.\d+)?')
      if '美' in string:
        return float(re.search(pattern, string).group()) * 10000 * 6.4397
      else:
        return float(re.search(pattern, string).group()) * 10000
    except Exception as e:
      print(f'解析价格时出错:{e}')
      return 0
  else:
    return 0

def parse_seprate(string:str, seprate:str):
  results = set()
  result_str = ''
  if isinstance(string,str):
    try:
      items = string.split(seprate)
      for item in items:
        if item == '-' or item == ' - ':
          continue
        else:
          results.add(item)
      for s in results:
        result_str += s + ','
      return result_str.strip(',')
    except Exception as e:
      print(f'拆分字符串时出错{e}')
      return ''
  else:
    return ''

def get_date(string:str):
  if isinstance(string,str):
    try:
      pattern = re.compile(r'\d{4}-\d{1,2}-\d{1,2}')
      string = re.search(pattern, string).group()
      if string:
        return datetime.datetime.strptime(string, '%Y-%m-%d')
      else:
        return None
    except Exception as e:
      print(e)
      return None
  else:
    return None

def get_days(string:str):
  if isinstance(string,str):
    if '无' in string:
      return 0
    pattern = re.compile(r'\d{4}-\d{1,2}-\d{1,2}')
    dates = re.search(pattern, string).groups()
    if len(dates) >= 2:
      startdate = datetime.datetime.strptime(dates[0], '%Y-%m-%d')
      enddate = datetime.datetime.strptime(dates[1], '%Y-%m-%d')
      timedelta = enddate - startdate
      days  = timedelta.days()
      return days
    else:
      return 0
  else:
    return 0

def get_area(province:str,city:str,county:str):
  if county in consts.all_county:
    return consts.all_county[county]
  elif city in consts.all_city:
    return consts.all_city[city]
  elif province in consts.all_province:
    return consts.all_province[province]
  else:
    return None, None, None

def get_industry(string:str, industry_map=consts.all_industry):
  if isinstance(string,str):
    if string in industry_map['c']:
      return industry_map['c'][string]
    elif string in industry_map['b']:
      return industry_map['b'][string]
    elif string in industry_map['a']:
      return industry_map['a'][string]
    else:
      print(string)
      return None, None, None
  else:
    return None, None, None

def get_compType(string:str):
  result = []
  if isinstance(string,str):
    for key, value in consts.all_compTypes.items():
      if key in string:
        result.append(value)
      else:
        continue
  return result
