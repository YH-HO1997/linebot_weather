import json
import requests
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi('')
handler = WebhookHandler('')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def weather(city):
    # cities=['臺北','新北','桃園','臺中','臺南', '高雄', '基隆','新竹']
    # counties=['宜蘭', '花蓮', '臺東', '澎湖', '金門', '連江','苗栗', '彰化', '南投', '雲林'
    #           , '嘉義', '屏東']
    city = city.replace('台', '臺')
    try:
        res = get(city)
    except Exception as e:
        return f'程式執行錯誤，{e}'
    else:
        return f"""{city}，{res[0][1]["startTime"]}~{res[0][1]["endTime"]}，
天氣狀況: {res[0][1]["parameter"]["parameterName"]}
降雨機率: {res[0][3]["parameter"]["parameterName"]}%
最高溫: {res[0][9]["parameter"]["parameterName"]}，最低溫:{res[0][5]["parameter"]["parameterName"]}度
舒適度: {res[0][7]["parameter"]["parameterName"]}
"""

def get(city):
    token = ''  # 剛生成的 Token
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + \
        token + '&format=JSON&locationName=' + str(city)
    Data = requests.get(url)
    Data = (json.loads(Data.text))['records']['location'][0]['weatherElement']
    # 讀取以上格式資料即可
    res = [[], [], []]  # 36小時資料切成3份
    for j in range(len(res)):
        for i in Data:
            res[j].append(i['elementName'])
            res[j].append(i['time'][j])  # 'time'為字典的陣列，加入同一時段開始時間、結束時間與天氣(字典)等資訊
    return res

@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    message=event.message.text
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=weather(message)))

if __name__ == "__main__":
    app.run()