from datetime import date, datetime, timedelta
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import requests
import os
import random
import json

nowtime = datetime.utcnow() + timedelta(hours=8)  
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d")

app_id = os.getenv("APP_ID")
app_secret = os.getenv("APP_SECRET")
template_id = os.getenv("TEMPLATE_ID")

def get_time():
    dictDate = {'Monday': '星期一', 'Tuesday': '星期二', 'Wednesday': '星期三', 'Thursday': '星期四',
                'Friday': '星期五', 'Saturday': '星期六', 'Sunday': '星期天'}
    a = dictDate[nowtime.strftime('%A')]
    return nowtime.strftime("%Y年%m月%d日 %H时%M分 ")+ a

def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']

def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)

def get_weather(city):
    url = "https://v0.yiketianqi.com/api?unescape=1&version=v91&appid=43656176&appsecret=I42og6Lm&city=" + city
    res = requests.get(url).json()
    weather = res['data'][0]
    return weather

def get_count(born_date):
    delta = today - datetime.strptime(born_date, "%Y-%m-%d")
    return delta.days


def get_birthday(birthday, year, today):
    birthday_year = birthday.split("-")[0]
    # 判断是否为农历生日
    if birthday_year[0] == "r":
        r_mouth = int(birthday.split("-")[1])
        r_day = int(birthday.split("-")[2])
        # 获取农历生日的今年对应的月和日
        try:
            birthday = ZhDate(year, r_mouth, r_day).to_datetime().date()
        except TypeError:
            print("请检查生日的日子是否在今年存在")
            os.system("pause")
            sys.exit(1)
        birthday_month = birthday.month
        birthday_day = birthday.day
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)
 
    else:
        # 获取国历生日的今年对应月和日
        birthday_month = int(birthday.split("-")[1])
        birthday_day = int(birthday.split("-")[2])
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today > year_date:
        if birthday_year[0] == "r":
            # 获取农历明年生日的月和日
            r_last_birthday = ZhDate((year + 1), r_mouth, r_day).to_datetime().date()
            birth_date = date((year + 1), r_last_birthday.month, r_last_birthday.day)
        else:
            birth_date = date((year + 1), birthday_month, birthday_day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    elif today == year_date:
        birth_day = 0
    else:
        birth_date = year_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    return birth_day

client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)

f = open("./users_info.json", encoding="utf-8")
js_text = json.load(f)
f.close()
data = js_text['data']
num = 0
for user_info in data:
    born_date = user_info['born_date']
    birthday = born_date[5:]
    city = user_info['city']
    user_id = user_info['user_id']
    name=' 【'+user_info['user_name'].upper()+'】 '
    
    weather= get_weather(city)

    data = dict()
    data['time'] = {
        'value': get_time(), 
        'color':'#470024'
        }
    data['words'] = {
        'value': get_words(), 
        'color': get_random_color()
        }
    data['weather'] = {
        'value': weather['wea'], 
        'color': '#002fa4'
        }
    data['city'] = {
        'value': city, 
        'color': get_random_color()
        }
    data['tem_high'] = {
        'value': weather['tem1'], 
        'color': '#D44848'
        }
    data['tem_low'] = {
        'value': weather['tem2'], 
        'color': '#01847F'
        }
    data['born_days'] = {
        'value': get_count(born_date), 
        'color': get_random_color()
        }
    data['birthday_left'] = {
        'value': get_birthday(birthday), 
        'color': get_random_color()
        }
    data['air'] = {
        'value': weather['air_level'], 
        'color': get_random_color()
        }
    data['wind'] = {
        'value': weather['win'][0], 
        'color': get_random_color()
        }
    data['name'] = {
        'value': name, 
        'color': get_random_color()
        }
    data['uv'] = {
        'value': weather['uvDescription'], 
        'color': get_random_color()
        }
    
    res = wm.send_template(user_id, template_id, data,'https://froan.cn')
    print(res)
    num += 1
print(num)
