from lxml import etree
import datetime
from datetime import timedelta
import requests
import re


# 将字符串类型的日期转换为datetime.date类型的日期
def parse_ymd(s):
    year_s, mon_s, day_s = s.split('-')
    return datetime.date(int(year_s), int(mon_s), int(day_s))


# 伪装成浏览器（UA伪装）：将对应的User-Agent封装到一个字典中
headers = {
     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
 }


# 获得内蒙古卫健委新闻发布首页网页源码文件
url_firstPage = 'http://wjw.nmg.gov.cn/xwzx/xwfb/index.html'
response = requests.get(url=url_firstPage, headers=headers)
response.encoding = "UTF-8"
page_text = response.text
with open('NHC.html', 'w', encoding="UTF-8") as fp:
    fp.write(page_text)


# 获得当前日期的前三趟航班(每周五的航班)
flight_list = list()
today = datetime.date.today()
if today.weekday() < 4:
    offset = (today.weekday() - 4) % 7
    friday = today - timedelta(days=offset)
else:
    offset = today.weekday() % 4
    friday = today - timedelta(days=offset)
for i in range(0, 3):
    flight_list.insert(i, friday - timedelta(days=7*i))

# 接收用户指令，获得指定航班日期date1
print("最近起飞的三趟航班分别是：", flight_list[0], flight_list[1], flight_list[2])
date1 = input("请输入需要查看航班日期，格式20XX-MM-DD：")
date1 = parse_ymd(date1)


# 获得用户输入的航班日期入境前后情况通报新闻链接
url1 = 'http://wjw.nmg.gov.cn/xwzx/xwfb'  # 目标网页链接的头部
url_before = 'none'   # 入境前网页链接
url_after = 'none'    # 入境后网页链接

parser1 = etree.HTMLParser(encoding="utf-8")  # 避免html文件不规范导致解析错误，增加该语句
tree1 = etree.parse('NHC.html', parser=parser1)  # 实例化一个etree对象
date2 = tree1.xpath('/html//div[@class="g_xwfbli"]/ul//span/text()')  # 获取span标签下的内容（公告发布日期）
url2 = tree1.xpath('/html//div[@class="g_xwfbli"]/ul//a/@href')     # 获取a标签的href属性值（目标网页链接的尾部）
for i in range(0, len(date2)-1):
    release_date = parse_ymd(str(date2[i])[1:-1])  # 获取公告发布日期
    announcement_date = release_date - timedelta(days=1)  # 公告日期
    if date1 == announcement_date:
        url_before = url1 + str(url2[i])[1:]
    elif date1 == announcement_date - timedelta(days=1):
        url_after = url1 + str(url2[i])[1:]

# 内容分析
content_before = list()
content_after = list()
tree_before = etree.parse(url_before, parser=parser1)
tree_after = etree.parse(url_after, parser=parser1)
content_before_temp = tree_before.xpath('/html/body//div[@class="view TRS_UEDITOR trs_paper_default trs_web"]//span/text()')
content_after_temp = tree_after.xpath('/html/body//div[@class="view TRS_UEDITOR trs_paper_default trs_web"]//span/text()')
for i in range(0, len(content_before_temp)):
    content_before.insert(i, str(content_before_temp[i]))
situation_before = re.findall(r"境外输入(.+?)（均在呼和浩特市）。", content_before[-1])
for i in range(0, len(content_after_temp)):
    content_after.insert(i, str(content_after_temp[i]))
situation_after = re.findall(r"境外输入(.+?)（均在呼和浩特市）。", content_after[-1])
str1 = ','
print("该航班入境前呼和浩特市相关情况是：现有境外输入", str1.join(situation_before))
print("该航班入境后呼和浩特市相关情况是：现有境外输入", str1.join(situation_after))
