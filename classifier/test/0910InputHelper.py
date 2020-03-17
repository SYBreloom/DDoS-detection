# coding=utf-8

# Author: $￥
# @Time: 2019/9/10 18:06

import json
import numpy as np


# todo 参考这个之前的InputHelper 处理log文件 获取训练样本数据

#这个文件/函数用于处理输入，作为sflow和pkt-in输入的接口，处理文件的特征信息
# 1.读取 2.归一化 3.筛选获取特征集


# 其中attack_files是一个包含n个list的list，内层的应该包含偶数个文件 normal_file同样
# 输入要求如下
# sflow_files[0] = [ sflowfile_1, sflowfile_2, ..., sflowfile_n ] 一共n个
# pktin_files[1] = [ pkt-infile_1, pkt-in_file_2, ..., pkt-in_file_n ] 一共n个
# label_list = [True or False] 一共n个
# switch_name 交换机名称
def load_dataset(sflow_files, pktin_files, label_list, switch_name):
    if switch_name != "s5" and switch_name != "s7":
        print("交换机名称错误")
        return

    if len(sflow_files) != len(pktin_files) or len(sflow_files) != len(label_list):
        print("文件输入长度木有对齐")
        return

    labels = []  # 保存labels
    input = []  # 保存从文件输入的矩阵，每一行是一个向量（需要归一化和不需要归一化的 合并结果）
    list1 = []  # 保存不需要归一化的几个变量矩阵 每一行包含所有不需要的向量
    list2 = []  # 保存待归一化的几个变量矩阵 每一行包含所有需要的向量

    for i in range(len(sflow_files)):
        sflow_file = sflow_files[i]
        pktin_file = pktin_files[i]

        #文件里的sflow/packet-in信息，直接批量读进来
        record_list1 = []  # 获取sflow信息
        record_list2 = []  # 获取packet-in信息

        with open(file=sflow_file) as f:
            record_list1 = f.readlines()

        with open(file=pktin_file) as f:
            record_list2 = f.readlines()

        # 判断文件里的信息长度 取短的那个
        # 一般来说最后一行会出问题 直接不读了
        # record_length = min(len(record_list1), len(record_list2))-1
        if len(record_list1) < len(record_list2) or len(record_list1) > len(record_list2):
            print("文件信息长度不对等")
        record_length = min(len(record_list1), len(record_list2))-1

        for j in range(record_length):
            dict_sflow = json.loads(record_list1[j])
            dict_packetIn = json.loads(record_list2[j])

            # 这一块是s5和s7共有的部分
            srcIPEntropy_pktin = float(getAttributeFromSflowDict("srcIPEntropy", dict_packetIn))
            portSrcEntropy_pakin = getAttributeFromSflowDict("portSrcEntropy", dict_packetIn)
            avgPacketNum = getAttributeFromSflowDict("avgPacketNum", dict_packetIn)
            avgPacketLength = getAttributeFromSflowDict("avgPacketLength", dict_packetIn)

            ifOutUcastPkts = getAttributeFromSflowDict("ifOutUcastPkts", dict_sflow)
            ifOutOctets = getAttributeFromSflowDict("ifOutOctets", dict_sflow)
            ifInUcastPkts = getAttributeFromSflowDict("ifInUcastPkts", dict_sflow)
            ifInOctets = getAttributeFromSflowDict("ifInOctets", dict_sflow)

            # 获取s7的时候，从sflow那里多拿srcIPEntropy和portSrcEntropy这两个信息
            if switch_name == "s7":
                srcIPEntropy = getAttributeFromSflowDict("srcIPEntropy", dict_sflow)
                portSrcEntropy = getAttributeFromSflowDict("portSrcEntropy", dict_sflow)

                try:
                    # 取小数并保留2位数字
                    list1.append(list(map(lambda x: round(float(x), 2), (srcIPEntropy_pktin, portSrcEntropy_pakin, srcIPEntropy, portSrcEntropy))))  # 合成list并转化为float
                    list2.append((list(map(lambda x: round(float(x), 2), (avgPacketNum, ifOutUcastPkts, ifOutOctets, ifInUcastPkts, ifInOctets)))))
                    labels.append(label_list[i])
                except ValueError as e:
                    print(i, j)
                    print(ifOutOctets)
            elif switch_name == "s5":
                list1.append(list(map(lambda x: round(float(x), 2), (srcIPEntropy_pktin,))))
                list2.append(list(map(lambda x: round(float(x), 2), (avgPacketNum, ifOutUcastPkts, ifOutOctets, ifInUcastPkts, ifInOctets))))
                labels.append(label_list[i])

        return list1, list2, labels


def load_raw_dataset(sflow_files, pktin_files, label_list, switch_name):
    list1, list2, labels = load_dataset(sflow_files, pktin_files, label_list, switch_name)

    # 直接合并list1和list2
    raw_dataset = np.hstack((np.array(list1), np.array(list2)))  # 和concatenate（，axis=1）作用是一样的
    return raw_dataset, labels


# created in 19-05-14
def load_nomalized_dataset(sflow_files, pktin_files, label_list, switch_name):
    list1, list2, labels = load_dataset(sflow_files, pktin_files, label_list, switch_name)

    # 归一化list2 -> normalized_list2
    normalized_list2, max_values, min_values = normalize_input(np.array(list2))
    # 合并
    feature_lists = np.hstack((np.array(list1), normalized_list2))  # 和concatenate（，axis=1）作用是一样的

    return feature_lists, max_values, min_values, labels


def getAttributeFromSflowDict(attr, dict, default=0):
    try:
        att = dict[attr]
        # att = float(att.replace(',', ''))  # 之前写的时候我也不知为什么需要replace 自己实验的地方是用的int
    except Exception as e:
        print(e)
        print("get " + attr + " wrong!")
        att = default
    return att


def normalize_input(a):
    # two-dimension input
    # normalize by (a-min)/(max-min)
    a_norm = (a-a.min(axis=0)) / (a.max(axis=0)-a.min(axis=0))
    # print(a_norm)
    # 返回值保留两位小数
    return np.round(a_norm, 2), a.max(axis=0), a.min(axis=0)