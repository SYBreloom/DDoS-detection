# coding=utf-8

# Author: $￥
# @Time: 2019/9/10 14:42

from sklearn.svm import SVC
import numpy as np
from sklearn.externals import joblib

from P2reader import load_p2_dataset
from P1reader import load_p1_dataset
from Log_reader_helper import *


def train_svm(X_train, Y_train, output_model):
    # 初始化svm 获取核函数
    svm = SVC(kernel='linear', C=1.0, random_state=0)

    svm.fit(X_train, Y_train)
    joblib.dump(svm, output_model)

def P1_tarin():
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

    train_svm(feature_lists, label, r"svm_model.m")
    np.save("c", min_values)
    np.save("svm_max", max_values)


def P2_train():
    file1 = unicode(r"F:\近期文件\tmp\P1_attack.txt", 'utf-8')
    file2 = unicode(r"F:\近期文件\tmp\P1_normal.txt", 'utf-8')

    data_attack, label_attack = load_p1_dataset(file1, label=1)
    data_normal, label_normal = load_p1_dataset(file2, label=-1)

    data = data_attack + data_normal
    label = label_attack + label_normal

    data_need_no_normalize = [i[0:4] for i in data]  # P1的前4个不需要normalization
    data_need_normalize = [i[4:] for i in data]  # 后面的几个需要normalization

    normalized_list, max_values, min_values = normalize_input(np.array(data_need_normalize))

    feature_lists = np.hstack((np.array(data_need_no_normalize), normalized_list))  # 和concatenate（axis=1）作用是一样的

    train_svm(feature_lists, label, r"P1/svm_model.m")
    np.save("P1/svm_min", min_values)
    np.save("P1/svm_max", max_values)


if __name__ == "__main__":
    P2_train()

