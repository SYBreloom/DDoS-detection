# coding=utf-8

# Author: $￥
# @Time: 2019/9/5 15:41

from pox.core import core

from pox.lib.revent.revent import EventMixin  # 发布事件需要继承自这个类
from pox.lib.revent.revent import Event  # 时间监听需要
import time
import datetime
import imp

log = core.getLogger()


# 用来测试的工具类
class MyEvent(Event):
    def __init__(self, attr="no_attr"):
        Event.__init__(self)
        print("packetInCome")
        self.attr1 = attr
        # Author: $￥
        # @Time: 2019/10/7 13:39
        # 这个没啥用


class MyEvent2(Event):
    def __init__(self, attr="no_attr"):
        Event.__init__(self)
        self.attr1 = attr
        # Author: $￥
        # @Time: 2019/10/7 13:39
        # 测试event

# 组装好了的packetIn
class MaturePacketIn(Event):
    def __init__(self, srcIP, dstIP, portSrc, portDst):
        Event.__init__(self)
        self.srcIP = srcIP
        self.dstIP = dstIP
        self.portSrc = portSrc
        self.portDst = portDst


class TestEvent(Event):
    def __init__(self, msg="default"):
        Event.__init__(self)
        self.msg = msg
        log.info("P1 no alert: %s" % msg)


class P1Alert(Event):
    def __init__(self, switch_dpid, host_id):
        Event.__init__(self)

        self.switch_dpid = switch_dpid
        self.host_id = host_id
        imp.acquire_lock()
        now_time = datetime.datetime.now().strftime('%H:%M:%S.%f')
        imp.release_lock()

        log.info("P1 alert: %s " % now_time)
        with open(r"/home/sy/P1_delay.txt", 'a+') as f:
            # 考虑启线程写
            f.write("P1 alert: %s \n" % now_time)


class P2Alert(Event):
    def __init__(self, msg):
        self._msg = msg

        imp.acquire_lock()
        now_time = datetime.datetime.now().strftime('%H:%M:%S.%f')
        imp.release_lock()

        log.info("P2 alert: %s " % now_time)
        with open(r"/home/sy/P2_delay.txt", 'a+') as f:
            # 考虑启线程写
            f.write("P2 alert: %s \n" % now_time)
