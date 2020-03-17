# coding=utf-8

# Author: $￥
# @Time: 2019/9/19 11:10

import numpy as np


def normalize_input(a):
    # two-dimension input
    # normalize by (a-min)/(max-min)
    a_norm = (a-a.min(axis=0)) / (a.max(axis=0)-a.min(axis=0))
    # print(a_norm)
    # 返回值保留两位小数
    return np.round(a_norm, 2), a.max(axis=0), a.min(axis=0)


# 从dict里面判断是否存在attr，返回对应的值
def get_attribute_from_dict(dict, attr, default=0):
    try:
        att = dict[attr]
    except Exception as e:
        print(e)
        print("get " + attr + " wrong!")
        att = default
    return att


# 已知input_vector，对其进行min-max标准化
def normalize_vector(input_vector, min_value, max_value):
    normalized_output = (input_vector-min_value) / (max_value - min_value)
    return normalized_output
