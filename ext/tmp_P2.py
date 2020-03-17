# coding=utf-8

# Author: $￥
# @Time: 2019/9/12 14:59

from pox.core import core
from pox.lib.revent.revent import EventMixin
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
import imp
from MyEventLib import TestEvent
import datetime

log = core.getLogger()
INTERVAL = 3
count = 0


class Phase2 (EventMixin):
    _eventMixin_events = set([TestEvent])  # 定义事件列表

    def __init__(self):
        EventMixin.__init__(self)
        core.pktinHandler.addListeners(self)  # 监听pktinHandler
        # core.Phase1.addListeners(self)  # 监听phase1 是否进入phase2的检测
        # core.openflow.addListeners(self)  # 监听openflow的stats_信息

    def _handle_P1Alert(self, P1Alert):
        # todo 处理P1阶段过来的警告
        pass

    def _timer_func(self):
        print datetime.datetime.now().strftime('%H:%M:%S.%f')
        self.raiseEvent(TestEvent("test"))
        global count
        count += 1
        log.info(count)
        if count > 5:
            count = 0
            return False

    def _handle_FlowStatsReceived(self, flow_stats_received):
        # todo 统计需要监听的端口的流量信息
        pass

    def _handle_MaturePacketIn(self, maturePacketIn):
        # 时间窗口统计等等
        # log.info("receive mature packet in")
        global packet_in_counter

        imp.acquire_lock()

        packet_in_counter += 1
        # update_dict(packet_in_srcIP, maturePacketIn.srcIP)
        # update_dict(packet_in_dstIP, maturePacketIn.dstIP)
        # # 这里port用
        # update_dict(packet_in_srcPort, maturePacketIn.portSrc)
        # update_dict(packet_in_dstPort, maturePacketIn.portDst)

        imp.release_lock()


def launch():
    from pox.lib.recoco import Timer
    core.registerNew(Phase2)

    imp.acquire_lock()
    now_time = datetime.datetime.now().strftime('%H:%M:%S.%f')
    imp.release_lock()
    print(now_time + "lalala")

    # 如果我需要做实时的，这里的timer_func应该就需要根据事件的触发进行响应；否则为了检测率可以直接就是一直监控s7，不听事件
    global INTERVAL
    Timer(INTERVAL, core.Phase2._timer_func, recurring=True, selfStoppable=True)
