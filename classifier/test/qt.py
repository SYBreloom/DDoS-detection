# coding=utf-8

# Author: $￥
# @Time: 2019/9/10 15:16

from sklearn.svm import SVC
import numpy as np
import math
from sklearn.externals import joblib

import json
import requests
from classifier.P2reader import *
from classifier.Log_reader_helper import *

# sflow_url = r"http://192.168.203.156:8008/metric/192.168.203.148/json"
# r = requests.get(sflow_url)
# print(r.text)
# decoded = json.loads(r.text)
#
# print(decoded['36.ifoutpkts'])
# #     # 36是s7（122）  38是s8（124）
# # metrics = ["36.ifoutpkts", "36.ifoutoctets", "38.ifoutpkts", "38.ifoutoctets"]
#
# print(type(decoded))
# print(decoded)


som_map_list = np.load("../P2/som_map_list.npy")

som_weightages = np.load("../P2/som_weightages.npy")
labels = np.load("../P2/som_label.npy")

# 用于min-max normalization
som_min = np.load("../P2/som_min.npy")
som_max = np.load("../P2/som_max.npy")


def neuron_location(m, n):
    for i in range(m):
        for j in range(n):
            yield np.array([i, j])


def map_vects(input_vecors, weightage_vect, m, n):
    location_vects = np.array(list(neuron_location(m, n)))

    to_return = []
    for vector in input_vecors:
        min_index = min([i for i in range(len(weightage_vect))],
                        key=lambda x: np.linalg.norm(vector - weightage_vect[x]))

        to_return.append(location_vects[min_index])
    return to_return

'''
    file1 = unicode(r"F:\近期文件\tmp\P2_attack.txt", 'utf-8')
    file2 = unicode(r"F:\近期文件\tmp\P2_normal.txt", 'utf-8')

    data_attack, label_attack = load_p2_dataset(file1, label=1)
    data_normal, label_normal = load_p2_dataset(file2, label=-1)

    data = data_attack + data_normal
    label = label_attack + label_normal  # 读取log文件的时候，读取label数据

    data_need_normalize = [i[0:4] for i in data]  # P2的前四个需要normalization
    data_need_no_normalize = [i[4:] for i in data]  # 后面的几个不需要normalization

    normalized_list, max_values, min_values = normalize_input(np.array(data_need_normalize))

    X_train = np.hstack((normalized_list, np.array(data_need_no_normalize)))  # 和concatenate（axis=1）作用是一样的

    location_vects = np.array(list(neuron_location(20, 10)))  # 就是存放位置的list
'''

def timer_send():
    import os
    print os.system("ls")
    print(datetime.datetime.now().strftime('%H:%M:%S.%f'))

if __name__ == "__main__":

    import datetime
    import imp
    import threading
    now_time = datetime.datetime.now()

    # print "Enter time："+ time.strftime("%a %b %d %H:%M:%S", time.localtime())
    day_ = str(now_time.date().year) + '-' + str(now_time.date().month) + '-' + str(now_time.date().day)
    start_hour = now_time.hour
    start_min = now_time.minute + 2
    if start_min >= 60:
        start_min = start_min - 60
        start_hour = start_hour + 1

    imp.acquire_lock()
    start_time = datetime.datetime.strptime(day_ + " %s:%s:00" % (start_hour, start_min), "%Y-%m-%d %H:%M:%S")
    imp.release_lock()
    wait_seconds = (start_time - now_time).total_seconds()

    timer = threading.Timer(wait_seconds, timer_send, ())
    timer.start()
    timer.join()

