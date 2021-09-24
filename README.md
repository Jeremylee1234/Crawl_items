# Crawl_items
重构全网行业法拍爬虫

# 数据处理说明:
* 通过在process_item函数体中添加执行其他函数来对item进行进一步处理
  * 传入process_item函数中的item对象的各属性必须符合item.py要求
  * 成交项目所需字段：
    * 中标人姓名
    * 竞价次数
    * 最后成交价
    * 成交过程及时间间隔

# 已知bug
* data_formate中now为全局变量导致其值不会随真实时间而更新,会导致计算错误
* utils.py中对于二次处理item的函数需要修正
* ali_sf中当更新cookie后若全部更新失败会导致错误
* err_tims需要进一步进行全面的检查
* 若id不使用数据表自增创建而自行指定，则在数据库commit失败时可能导致的itemid不同表不一致现象需要合理的itemid确认机制来规避之
* 需要找到新的模拟登陆方式