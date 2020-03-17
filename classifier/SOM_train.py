# coding=utf-8

# Author: $￥
# @Time: 2019/9/9 10:33

#  这个文件是从LFA那个实验里面拿过来的，没有用tensorflow去实现SOM，简单的numpy
from numpy import *
import numpy as np
import time
import matplotlib.pyplot as plt

from P2reader import load_p2_dataset
from P1reader import load_p1_dataset
from Log_reader_helper import *


class SOMnet(object):
    def __init__(self, m, n, dim, n_iterations=1000):  # 设计网络参数初始值

        self.Steps = n_iterations  # 迭代次数
        self.w = []  # 权重向量组
        self.m = m
        self.n = n
        self.dim = dim
        self.alpha = 0.8  # 初始学习率
        self.sigma = max(m, n) / 2.0  # 初始影响半径

        self.dataMat = []  # 外部导入数据集
        self.classLabel = []  # 聚类后的类别标签
        self._weightage_vect = np.random.normal(size=[m * n, dim])
        self._location_vects = np.array(list(self._neuron_locations(self.m, self.n)))  # 就是存放位置的list

    def _neuron_locations(self, m, n):
        """
        Yields one by one the 2-D locations of the individual neurons
        in the SOM.
        """
        # Nested iterations over both dimensions
        # to generate all 2-D locations in the map
        for i in range(m):
            for j in range(n):
                yield np.array([i, j])

    def init_grid(self):  # 初始化第二层网络
        self._weightage_vect = np.array(np.random.rand(self.m * self.n, self.dim))

    def trainSOM(self):  # SOM网络的实现
        dm, dn = shape(self.dataMat)  # 1. 构建输入层网络

        for iter_no in arange(self.Steps):

            # 提示输出进度
            tenPercent = self.Steps / 10
            if iter_no % tenPercent == 0:
                print("%s percents finished" % (iter_no / tenPercent * 10), iter_no)

            shuffled_input_vects = self.dataMat.copy()
            np.random.shuffle(shuffled_input_vects)
            for input_vect in shuffled_input_vects:
                # 计算，根据欧式距离得到bmu
                vect_input_tensor = np.stack([input_vect for i in range(self.m * self.n)])
                difference = np.subtract(vect_input_tensor, self._weightage_vect)
                bmu_index = np.argmin(np.linalg.norm(difference, axis=1))

                # 找到这个bmu_index对应于矩阵的位置，也可以直接去_neuron_locations里面找对应的值，
                bmu_loc = np.array([bmu_index // self.m, bmu_index % self.m])

                # 更新学习率
                interation_decay = np.subtract(1.0, np.divide(iter_no,
                                                              self.Steps))
                _alpha_op = np.multiply(self.alpha, interation_decay)  # 学习率
                _sigma_op = np.multiply(self.sigma, interation_decay)  # 影响半径

                # 计算其它神经元到bmu的距离
                bmu_location_matrix = np.stack([bmu_loc for i in range(self.m * self.n)])
                bmu_distance_matrix = np.linalg.norm(np.subtract(bmu_location_matrix, self._location_vects), axis=1)

                neighbourhood_func = np.exp(np.negative(
                    np.divide(np.power(bmu_distance_matrix, 2), 2 * np.power(_sigma_op, 2))))
                # 用指数衰减的影响半径 这里和tf那里还不一样
                # exp(-(bmu_distance)^2 / 2*(sigma_op)^2 )

                greater = np.greater(bmu_distance_matrix, _sigma_op)

                learning_rate_op = np.where(greater,  # 在学习率之上，再根据距离调整学习量，即学习率*距离变量
                                            np.multiply(0.0, neighbourhood_func),
                                            np.multiply(_alpha_op, neighbourhood_func))
                learning_rate_multiplier = np.tile(np.reshape(learning_rate_op, (-1, 1)), self.dim)

                weightage_delta = np.multiply(
                    learning_rate_multiplier,
                    np.subtract(vect_input_tensor, self._weightage_vect))

                self._weightage_vect = np.add(self._weightage_vect, weightage_delta)

    '''
    def showCluster(self, plt):  # 绘图  显示聚类结果
        lst = unique(self.classLabel.tolist()[0])  # 去除
        i = 0
        for cindx in lst:
            myclass = nonzero(self.classLabel == cindx)[1]
            xx = self.dataMat[myclass].copy()
            if i == 0: plt.plot(xx[:, 0], xx[:, 1], 'bo')
            if i == 1: plt.plot(xx[:, 0], xx[:, 1], 'rd')
            if i == 2: plt.plot(xx[:, 0], xx[:, 1], 'gD')
            if i == 3: plt.plot(xx[:, 0], xx[:, 1], 'c^')
            i += 1
        plt.show()
    '''

    # 按照原来tf的那边，把这个方法重新拿过来
    # 找到vectors对应的输出层位置
    def map_vects(self, input_vecors):
        to_return = []
        for vector in input_vecors:
            min_index = min([i for i in range(len(self._weightage_vect))],
                            key=lambda x: np.linalg.norm(vector - self._weightage_vect[x]))

            to_return.append(self._location_vects[min_index])
        return to_return

    def get_weightages(self):
        return self._weightage_vect


def P2_train():
    # 几个参数
    M = 20
    N = 10
    dimension = 6

    global SOMnet
    SOMnet = SOMnet(M, N, dimension, n_iterations=8000)

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

    SOMnet.dataMat = X_train
    begin = time.time()
    SOMnet.trainSOM()
    print(time.time() - begin)  # 判断训练时间

    # 映射位置list
    map_list = SOMnet.map_vects(X_train)

    # 打出来看一下对应关系
    # for i in range(len(labels)):
    #     print(str( map_list[i].tolist()) + "   " + labels[i])

    # 保存1.normalized min-max 2.映射位置map_list 3.labels 4. weightages
    np.save("P2/som_min", min_values)
    np.save("P2/som_max", max_values)
    np.save("P2/som_weightages", SOMnet.get_weightages())
    np.save("P2/som_map_list", map_list)
    np.save("P2/som_label", np.array(label))


def P1_train():
    # 几个参数
    M = 20
    N = 10
    dimension = 7

    global SOMnet
    SOMnet = SOMnet(M, N, dimension, n_iterations=8000)

    file1 = unicode(r"F:\近期文件\tmp\P1_attack.txt", 'utf-8')
    file2 = unicode(r"F:\近期文件\tmp\P1_normal.txt", 'utf-8')

    data_attack, label_attack = load_p1_dataset(file1, label=1)
    data_normal, label_normal = load_p1_dataset(file2, label=-1)

    data = data_attack + data_normal
    label = label_attack + label_normal

    data_need_no_normalize = [i[0:4] for i in data]  # P1的前4个不需要normalization
    data_need_normalize = [i[4:] for i in data]  # 后面的几个需要normalization

    normalized_list, max_values, min_values = normalize_input(np.array(data_need_normalize))

    X_train = np.hstack((np.array(data_need_no_normalize), normalized_list))  # 和concatenate（axis=1）作用是一样的

    SOMnet.dataMat = X_train
    begin = time.time()
    SOMnet.trainSOM()
    print(time.time() - begin)  # 判断训练时间

    # 映射位置list
    map_list = SOMnet.map_vects(X_train)

    # 打出来看一下对应关系
    # for i in range(len(labels)):
    #     print(str( map_list[i].tolist()) + "   " + labels[i])

    # 保存1.normalized min-max 2.映射位置map_list 3.labels 4. weightages
    np.save("P1/som_min", min_values)
    np.save("P1/som_max", max_values)
    np.save("P1/som_weightages", SOMnet.get_weightages())
    np.save("P1/som_map_list", map_list)
    np.save("P1/som_label", np.array(label))


if __name__ == "__main__":
    # P1_train()
    P2_train()

