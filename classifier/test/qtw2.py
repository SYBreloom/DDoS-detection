# coding=utf-8

# Author: $￥
# @Time: 2019/10/8 10:35

import os
import threading

Interval = 3


def write_utilization():

    txt = os.system("ps aux | grep pox")

    with open(r"cpu_utilization", 'a+') as f:
        # 考虑启线程写
        f.write(str(txt) + " \n\n")
    timer = threading.Timer(Interval, write_utilization)
    timer.start()


if __name__ == "__main__":
    timer = threading.Timer(Interval, write_utilization)
    timer.start()