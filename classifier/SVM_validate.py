# coding=utf-8

# Author: $￥
# @Time: 2019/9/10 15:56


import numpy as np
from sklearn.externals import joblib
from classifier.EvaluationHelper import calculate_dr_fa

from Log_reader_helper import *
from P2reader import *
from P1reader import *


def P2_validate():
    # 读取模型
    svm_model = joblib.load(r"P2/svm_model.m")

    # 用于min-max normalization
    svm_min = np.load("P2/svm_min.npy")
    svm_max = np.load("P2/svm_max.npy")

    file = unicode(r"F:\近期文件\tmp\实验记录\0926出P2日志\P2_attack_10%.txt", 'utf-8')   # F:\近期文件\tmp\实验记录\0926出P2日志
    data_attack, expect_Y = load_p2_dataset(file, label=1)

    data_need_normalize = [i[0:4] for i in data_attack]  # P2的前四个需要normalization
    data_need_no_normalize = [i[4:] for i in data_attack]  # 后面的几个不需要normalization

    normalized_elements = normalize_vector(data_need_normalize, svm_min, svm_max)

    # 组装生成测试集
    test_X = np.hstack((normalized_elements, np.array(data_need_no_normalize)))  # 和concatenate（axis=1）作用是一样的

    # 输出测试标签
    predict_Y = svm_model.predict(test_X)

    # 把DR和FA 封了一个函数
    detection_rate, false_alarm = calculate_dr_fa(expect_Y, predict_Y)

def P1_validate():
    # 读取模型
    svm_model = joblib.load(r"P1/svm_model.m")

    # 用于min-max normalization
    svm_min = np.load("P1/svm_min.npy")
    svm_max = np.load("P1/svm_max.npy")

    file = unicode(r"F:\近期文件\tmp\实验记录\0930出P1日志\P1_normal.txt", 'utf-8')
    data_normal, expect_Y = load_p1_dataset(file, label=-1)

    data_need_no_normalize = [i[0:4] for i in data_normal]  # P1的前4个不需要normalization
    data_need_normalize = [i[4:] for i in data_normal]  # 后面的几个需要normalization

    normalized_elements = normalize_vector(data_need_normalize, svm_min, svm_max)

    # 组装生成测试集
    test_X = np.hstack((np.array(data_need_no_normalize), normalized_elements))  # 和concatenate（axis=1）作用是一样的

    # 输出测试标签
    predict_Y = svm_model.predict(test_X)

    # 把DR和FA 封了一个函数
    detection_rate, false_alarm = calculate_dr_fa(expect_Y, predict_Y)


if __name__ == "__main__":
    # P2_validate()
    P1_validate()


