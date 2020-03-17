# coding=utf-8

# Author: $￥
# @Time: 2019/9/10 18:11

import numpy as np
from EvaluationHelper import calculate_dr_fa

from P1reader import *
from P2reader import *
from Log_reader_helper import *


class Som_Knn(object):
    def __init__(self, weightages, train_maps, labels, m, n, k=20):
        self._weightages = weightages
        self._train_maps = train_maps
        self._labels = labels
        self._k = k
        self.m = m
        self.n = n

    def classify_KNN(self, input_vector):
        # input 判断的向量
        # dataSet 已有的数据集
        # label 数据集对应的标签
        # k 选取k个
        data_size = self._train_maps.shape[0]  # dataSet的向量的数目
        diff = self._train_maps - np.tile(input_vector, (data_size, 1))
        sqdiff = diff ** 2
        square_dist = np.sum(sqdiff, axis=1)  # 行向量分别相加，从而得到新的一个行向量
        dist = square_dist ** 0.5  # 开根号算距离

        # 对距离进行排序
        sorted_dist_index = np.argsort(dist)  # argsort()根据元素的值从大到小对元素进行排序，返回下标

        class_count = {}
        for i in range(self._k):
            vote_label = self._labels[sorted_dist_index[i]]
            class_count[vote_label] = class_count.get(vote_label, 0) + 1
        # 找到出现次数最多的类别
        max_count = 0
        for key, value in class_count.items():
            if value > max_count:
                max_count = value
                classes = key
        return classes

    def _neuron_location(self, m, n):
        for i in range(m):
            for j in range(n):
                yield np.array([i, j])

    def map_vector(self, input_vector):
        location_vects = np.array(list(self._neuron_location(self.m, self.n)))

        min_index = min([i for i in range(len(self._weightages))],
                        key=lambda x: np.linalg.norm(input_vector -
                                                     self._weightages[x]))
        return location_vects[min_index]

    def predict_single_vector(self, input_vector):
        # input_vector_norm = self.normalize_vector(input_vector)  # 归一化处理放在进入predict以前完成，归一化函数可以复用用于SVM_validate
        input_vector_mapped_loc = self.map_vector(input_vector)  # 计算对应的映射坐标
        classes = self.classify_KNN(input_vector_mapped_loc)  # 根据坐标，用KNN判断应该归类的类别和占比
        return classes

    def predict(self, input):
        to_return = []
        for i in input:
            classes = self.predict_single_vector(i)
            to_return.append(classes)
        return to_return


def P2_validate():
    # 1.读取模型 2.读取输入  3.标准化 4.模型判断输出标签 5.计算DR，FA

    # 1.读取模型
    som_weightages = np.load("P2/som_weightages.npy")
    som_map_list = np.load("P2/som_map_list.npy")
    labels = np.load("P2/som_label.npy")
    # 模型读取，这些都从训练好得到的文件里面直接读出来就好
    som_knn_model = Som_Knn(som_weightages, som_map_list, labels, m=20, n=10, k=10)

    # 用于min-max normalization
    som_min = np.load("P2/som_min.npy")
    som_max = np.load("P2/som_max.npy")

    # 2.读取log的输入
    file = unicode(r"F:\近期文件\tmp\实验记录\0926出P2日志\P2_normal_10rate.txt", 'utf-8')  # "F:\近期文件\tmp\P2_attack.txt"
    data_attack, expect_Y = load_p2_dataset(file, label=1)

    # 3.标准化
    data_need_normalize = [i[0:4] for i in data_attack]  # P2的前四个需要normalizationasadsa
    data_need_no_normalize = [i[4:] for i in data_attack]  # 后面的几个不需要normalization

    normalized_elements = normalize_vector(data_need_normalize, som_min, som_max)
    # 组装生成测试集
    test_X = np.hstack((normalized_elements, np.array(data_need_no_normalize)))  # 和concatenate（axis=1）作用是一样的

    # 4.模型判断输出标签
    predict_Y = som_knn_model.predict(test_X)

    # 5.计算DR，FA  这里把DR和FA 封了一个函数
    detection_rate, false_alarm = calculate_dr_fa(expect_Y, predict_Y)


def P1_validate():

    # 1.读取模型 2.读取输入  3.标准化 4.模型判断输出标签 5.计算DR，FA

    # 1.读取模型
    som_weightages = np.load("P1/som_weightages.npy")
    som_map_list = np.load("P1/som_map_list.npy")
    labels = np.load("P1/som_label.npy")
    # 模型读取，这些都从训练好得到的文件里面直接读出来就好
    som_knn_model = Som_Knn(som_weightages, som_map_list, labels, m=20, n=10, k=7)

    # 用于min-max normalization
    som_min = np.load("P1/som_min.npy")
    som_max = np.load("P1/som_max.npy")

    # 2.读取log的输入
    data_normal, expect_Y = load_p1_dataset(unicode(r"F:\近期文件\tmp\实验记录\0930出P1日志\P1_normal.txt", 'utf-8'), label=-1)
    # 3.标准化
    data_need_no_normalize = [i[0:4] for i in data_normal]  # P1的前4个不需要normalization
    data_need_normalize = [i[4:] for i in data_normal]  # 后面的几个需要normalization

    # data_attack, expect_Y = load_p1_dataset(unicode(r"F:\近期文件\tmp\P1_attack.txt", 'utf-8'), label=-1)
    # data_need_no_normalize = [i[0:4] for i in data_attack]  # P1的前4个不需要normalization
    # data_need_normalize = [i[4:] for i in data_attack]  # 后面的几个需要normalization

    normalized_elements = normalize_vector(data_need_normalize, som_min, som_max)
    # 组装生成测试集
    test_X = np.hstack((np.array(data_need_no_normalize), normalized_elements))  # 和concatenate（axis=1）作用是一样的

    # 4.模型判断输出标签
    predict_Y = som_knn_model.predict(test_X)

    # 5.计算DR，FA  这里把DR和FA 封了一个函数
    detection_rate, false_alarm = calculate_dr_fa(expect_Y, predict_Y)

    # todo 输出DR和FA


if __name__ == "__main__":
    P1_validate()
    # P2_validate()
