#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import alchemy as db

all_province, all_city, all_county = db.get_areas()

all_industry = db.get_industry()

all_compTypes = db.get_compTypes()