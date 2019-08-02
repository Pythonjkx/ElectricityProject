from __future__ import absolute_import
import json
import requests
from FreshShop.celery import app


@app.task
def taskExample():
    print('send email is ok!')

@app.task
def add(x=1,y=2):
    return x+y
@app.task
def DingTalk():
    print(1)
    url = 'https://oapi.dingtalk.com/robot/send?access_token=fa9d01aab4fb88478ff1e9fe8a084f90661ab98c3ef64e41d74f003c46dd5880'
    hearders = {
        'Content-Type':'application/json',
        'Chartset':'utf-8'
    }
    requests_data = {
        'msgtype':'text',
        'text':{
            'content':'风萧萧兮易水寒'
        },
        'at':{
            'atMobiles':[

            ],
        },
        'isAtAll':True
    }
    sendDate = json.dumps(requests_data)
    response = requests.post(url,hearders=hearders,data=sendDate)
    content = response.json()
    print(content)
