# coding=utf-8

# Author: $￥
# @Time: 2019/9/19 9:42

# 返回数据集data_list和label_list
# 输出读取的文件，json格式见下方，label为该文件指定的label，或者跟在每个的后面

import json
import numpy as np
from classifier.Log_reader_helper import get_attribute_from_dict
from Log_reader_helper import normalize_input

# 返回数据集data_list和label_list
# 输出读取的文件，json格式见下方，label为该文件指定的label，或者跟在每个的后面
# 如果后续需要更改读取内容，
def load_p1_dataset(file_name, label=None):

    with open(file_name, "r") as f:
        record_list = f.readlines()

    final_list = []
    label_list = []

    for i in record_list:
        if i == '\n':
            # 空行不读
            continue
        record_dict = json.loads(i)

        # 前四个变量都是entropy不需要min-max normalization 后面的几个需要
        sip = get_attribute_from_dict(record_dict, "sip")
        dip = get_attribute_from_dict(record_dict, "dip")
        sport = get_attribute_from_dict(record_dict, "sport")
        dport = get_attribute_from_dict(record_dict, "dport")
        pkt_num = get_attribute_from_dict(record_dict, "pkt_num")
        pkts_subnet5 = get_attribute_from_dict(record_dict, "pkts_subnet5")
        bytes_subnet5 = get_attribute_from_dict(record_dict, "bytes_subnet5")

        if label is None:
            label = get_attribute_from_dict(record_dict, "label")  # 这个可以在输出的时候加，也可以自己手动加载文档获取

        final_list.append((sip, dip, sport, dport, pkt_num, pkts_subnet5, bytes_subnet5))
        label_list.append(label)

    return final_list, label_list


if __name__ == "__main__":
    file1 = unicode(r"F:\近期文件\tmp\P1.txt", 'utf-8')

    data, label = load_p1_dataset(file1, label=1)

    # data = data1 + data2
    # label = label1 + label2

    # {"sip": 0.52, "dip": 0.52, "sport": 0, "dport": 0, "pkt_num": 346, "pkts_subnet5": 3.54, "bytes_subnet5": 347.21}
    data_need_no_normalize = [i[0:4] for i in data]  # P1的前四个（不!）需要normalization
    data_need_normalize = [i[4:] for i in data]  # 后面的几个需要normalization

    # normalize 前四个
    normalized_list, max_values, min_values = normalize_input(np.array(data_need_normalize))

    feature_lists = np.hstack((np.array(data_need_no_normalize), normalized_list))  # 和concatenate（axis=1）作用是一样的

    print(feature_lists)
