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

# 验证登陆：
1. 接管手机短信，验证码登陆网页移动端
   1. https://main.m.taobao.com/mytaobao/index.html?spm=a215s.7406091.toolbar.i0
2. 获取淘宝客户端中的cookie
3. 手机淘宝扫码登陆(DecryptLogin.login.Login().taobao()
   1. Python+UIautomator2控制手机实现自定义脚本
   2. 淘宝app登陆扫码不可通过图片扫码，只可手动扫描场景
4. 解决掉滑块验证率过低问题
5. 控制手机浏览器模拟网页登陆

## 暂定登陆方案:
1. 海外国际淘宝selenium模拟登陆
2. 国内普通淘宝selenium模拟登陆
   1. https://login.taobao.com/member/login.jhtml
3. 国内移动端网页淘宝手机验证码登陆
   1. 

根据需要每次需要更新Cookie时以合适的概率选择验证方式