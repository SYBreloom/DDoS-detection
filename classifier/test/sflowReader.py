# coding=utf-8

# Author: $￥
# @Time: 2019/9/18 16:28

import urllib
import requests
import json


# 从sflow-rt地址获取json的数据，
def sflow_read():

    url = r"http://192.168.203.156:8008/metric/192.168.203.148/json"
    r = requests.get(url)
    decoded = json.loads(r.text)

    # 36是s7（122）  38是s8（124）
    metrics = ["36.ifoutpkts", "36.ifoutoctets", "38.ifoutpkts", "38.ifoutoctets"]

    # 输出json的dict里面的metric
    for i in metrics:
        print(decoded[i])

    return decoded

    # 如果还要添加
    # 9->sub1  19->sub2  25->sub3  31->sub4

sflow_read()