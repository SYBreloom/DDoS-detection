# coding=utf-8

# Author: $￥
# @Time: 2019/9/10 18:50


def calculate_dr_fa(expect_Y, predict_Y):
    # 转成list比较各个值
    # 这里可能本身就是list的element 9.25偷懒了 感觉应该不会复用到了...吧...
    if type(expect_Y) != list:
        expect_Y_list = expect_Y.tolist()
    else:
        expect_Y_list = expect_Y

    if type(predict_Y) != list:
        predict_Y_list = predict_Y.tolist()
    else:
        predict_Y_list = predict_Y

    tp = 0
    tn = 0
    fp = 0
    fn = 0

    # 遍历计算
    for i in range(len(expect_Y_list)):
        if expect_Y_list[i] == -1:  # normal
            if predict_Y_list[i] == +1:
                fp += 1
            else:  # normal correctly identified
                tn += 1
        else:
            if predict_Y_list[i] == +1:
                tp += 1
            else:  # attack not identified
                fn += 1

    if (tp + fn) > 0:
        detection_rate = float(tp) / (tp+fn)
    else:
        detection_rate = None
    if (fp + tn) > 0:
        false_alarm = float(fp) / (fp + tn)
    else:
        false_alarm = None

    print(detection_rate, false_alarm)

    return detection_rate, false_alarm
