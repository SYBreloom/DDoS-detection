# coding=utf-8

# Author: $￥
# @Time: 2019/9/16 14:53

import math


# 给定dict,设置dict[key]的值
# 若之前不存在，设为value
# 若已存在，加value
def update_dict(dict, key, value=1):
    if key == '':
        return

    if key in dict:
        dict[key] = dict.get(key) + value
    else:
        dict.setdefault(key, value)


# 其实这里有很多前提条件需要判断，不为空、log真数为1影响normalize，底数为0等等
def calculate_entropy(input_dict):
    if len(input_dict) <= 1:
        return 0

    sum = 0
    entropy = 0

    for i, v in input_dict.items():
        assert v > 0  # 每一项均大于0
        sum += v
    for i, v in input_dict.items():
        tmp = float(v)/sum
        entropy -= tmp * math.log(tmp)

    # normalization 总数为1的时候会除零
    if sum > 1:
        return round(entropy / math.log(len(input_dict)), 2)  # 保留两位小数
    else:
        return 0


# 已知input_vector，对其进行min-max标准化
def normalize_vector(input_vector, min_value, max_value):
    normalized_output = (input_vector-min_value) / (max_value - min_value)
    return normalized_output