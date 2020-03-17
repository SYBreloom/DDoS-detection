# coding=utf-8

# Author: $￥
# @Time: 2019/9/10 15:56


import numpy as np
from sklearn.externals import joblib
from EntropyHelper import normalize_vector

def P2_validate(data_input):
    # 读取模型
    svm_model = joblib.load(r"ext/P2/svm_model.m")

    # 用于min-max normalization
    svm_min = np.load("ext/P2/svm_min.npy")
    svm_max = np.load("ext/P2/svm_max.npy")

    data_need_normalize = data_input[0:4]   # P2的前四个需要normalization
    data_need_no_normalize = data_input[4:]  # 后面的几个不需要normalization

    normalized_elements = normalize_vector(data_need_normalize, svm_min, svm_max)

    # 组装生成测试集
    test_X = np.hstack((normalized_elements, np.array(data_need_no_normalize)))  # 和concatenate（axis=1）作用是一样的

    # 输出测试标签
    predict_Y = svm_model.predict(test_X.reshape(1, -1))

    return predict_Y

def P1_validate(data_input):
    # 读取模型
    svm_model = joblib.load(r"ext/P1/svm_model.m")

    # 用于min-max normalization
    svm_min = np.load("ext/P1/svm_min.npy")
    svm_max = np.load("ext/P1/svm_max.npy")

    data_need_no_normalize = data_input[0:4]   # P1的前4个不需要normalization
    data_need_normalize = data_input[4:]  # 后面的几个需要normalization

    normalized_elements = normalize_vector(data_need_normalize, svm_min, svm_max)

    # 组装生成测试集
    test_X = np.hstack((np.array(data_need_no_normalize), normalized_elements))  # 和concatenate（axis=1）作用是一样的

    # 输出测试标签
    predict_Y = svm_model.predict(test_X.reshape(1, -1))
    return predict_Y


if __name__ == "__main__":
    # P2_validate()
    P1_validate()


