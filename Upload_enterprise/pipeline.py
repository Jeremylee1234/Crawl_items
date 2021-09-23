#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import alchemy as db
import utils

def pipeline(item:dict, seprate:str):
  try:
    industry = utils.get_industry(item['所属行业'])
    areas = utils.get_area(item['province'], item['city'], item['county'])
    new_enterprise = db.Enterprise(
      enterprise = utils.get_str(item['公司名称']),
      status = utils.get_status(item['经营状态']),
      represent = utils.get_str(item['法定代表人']),
      regCaps = utils.get_money(item['注册资本']),
      payCaps = utils.get_money(item['实缴资本']),
      estabDate = utils.get_date(item['成立日期']),
      approveDate = utils.get_date(item['核准日期']),
      operatePeriod = utils.get_days(item['营业期限']),
      creditCode = utils.get_str(item['统一社会信用代码']),
      taxpayerCode = utils.get_str(item['纳税人识别号']),
      regCode = utils.get_str(item['注册号']),
      orzCode = utils.get_str(item['组织机构代码']),
      insuranceNum = utils.get_int(item['参保人数']),
      emails = utils.parse_seprate(item['联系邮箱'],seprate),
      phones = utils.parse_seprate(item['联系电话'],seprate),
      formerName = utils.get_str(item['曾用名']),
      engName = utils.get_str(item['英文名']),
      website = utils.get_str(item['网址']),
      address = utils.get_str(item['注册地址']),
      latestAddr = utils.get_str(item['最新地址']),
      scopes = utils.get_str(item['经营范围']),
      compTypes = utils.get_compType(item['企业类型']),
      compTypes_content = utils.get_str(item['企业类型']),
      provinceId = areas[0],
      cityId = areas[1],
      countyId = areas[2],
      industryId_a = industry[0],
      industryId_b = industry[1],
      industryId_c = industry[2]
    )
    try:
      db.db_session.add(new_enterprise)
      db.db_session.commit()
      return True
    except Exception as e:
      db.db_session.rollback()
      print(f'数据库提交时出错:{e}')
      return False
  except Exception as e:
    print(f'数据处理时出错:{e}')
    return False