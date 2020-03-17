# coding=utf-8

# Author: $￥
# @Time: 2019/9/17 19:45

import json
import numpy as np


# 返回数据集data_list和label_list
# 输出读取的文件，json格式见下方，label为该文件指定的label，或者跟在每个的后面
def load_p2_dataset(file_name, label=None):

    with open(file_name, "r") as f:
        record_list = f.readlines()

    final_list = []
    label_list = []

    for i in record_list:
        if i == '\n':
            # 空行不读
            continue
        record_dict = json.loads(i)

        # 前四个变量需要min-max normalizaton 后面的entropy不需要

        byte_rate = get_attribute_from_dict(record_dict, "byte_rate")
        pkt_rate = get_attribute_from_dict(record_dict, "pkt_rate")
        active_src_ip = get_attribute_from_dict(record_dict, "active_src_ip")
        active_src_port = get_attribute_from_dict(record_dict, "active_src_port")
        byte_count_entropy = get_attribute_from_dict(record_dict, "byte_count_entropy")
        pkt_count_entropy = get_attribute_from_dict(record_dict, "pkt_count_entropy")

        if label is None:
            label = get_attribute_from_dict(record_dict, "label")  # 这个可以在输出的时候加，也可以自己手动加载文档获取

        final_list.append((byte_rate, pkt_rate, active_src_ip, active_src_port, byte_count_entropy, pkt_count_entropy))
        label_list.append(label)

    return final_list, label_list


# 从dict里面判断是否存在attr，返回对应的值
def get_attribute_from_dict(dict, attr, default=0):
    try:
        att = dict[attr]
    except Exception as e:
        print(e)
        print("get " + attr + " wrong!")
        att = default
    return att


if __name__ == "__main__":

    from classifier.Log_reader_helper import normalize_input

    # if __name__ == "__main__":
    #     file1 = unicode(r"F:\近期文件\tmp\P2_1.txt", 'utf-8')
    #     file2 = unicode(r"F:\近期文件\tmp\P2_2.txt", 'utf-8')
    #
    #     data1, label1 = load_p2_dataset(file1, label=1)
    #     data2, label2 = load_p2_dataset(file2, label=-1)
    #
    #     data = data1 + data2
    #     label = label1 + label2
    #
    #     # {"byte_rate": 533.33, "pkt_rate": 2.0, "active_src_ip": 3, "active_src_port": 3,
    #     # "byte_count_entropy": 0.08, "pkt_count_entropy": 0.56}
    #     data_need_normalize = [i[0:4] for i in data]  # P2的前四个需要normalization
    #     data_need_no_normalize = [i[4:] for i in data]  # 后面的几个不需要normalization
    #
    #     # normalize 前四个
    #     normalized_list, max_values, min_values = normalize_input(np.array(data_need_normalize))
    #
    #     feature_lists = np.hstack((normalized_list, np.array(data_need_no_normalize)))  # 和concatenate（axis=1）作用是一样的
    #
    #     print(feature_lists)

    if __name__ == "__main__":
        file1 = unicode(r"F:\近期文件\tmp\P2_attack.txt", 'utf-8')
        file2 = unicode(r"F:\近期文件\tmp\P2_normal.txt", 'utf-8')

        data_attack, label_attack = load_p2_dataset(file1, label=1)
        data_normal, label_normal = load_p2_dataset(file2, label=-1)

        data = data_attack + data_normal
        label = label_attack + label_normal

        data_need_normalize = [i[0:4] for i in data]  # P2的前四个需要normalization
        data_need_no_normalize = [i[4:] for i in data]  # 后面的几个不需要normalization

        normalized_list, max_values, min_values = normalize_input(np.array(data_need_normalize))

        feature_lists = np.hstack((normalized_list, np.array(data_need_no_normalize)))  # 和concatenate（axis=1）作用是一样的
