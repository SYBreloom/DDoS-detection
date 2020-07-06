# coding=utf-8

# Author: $￥
# @Time: 2019/9/5 16:02

from pox.core import core
from pox.lib.revent.revent import EventMixin
from MyEventLib import TestEvent, P1Alert
import imp
import json
import collections
import requests
from requests.exceptions import ConnectionError
from EntropyHelper import calculate_entropy, update_dict

INTERVAL = 5

log = core.getLogger()

packet_in_counter = 0
packet_in_srcIP = dict()
packet_in_dstIP = dict()
packet_in_srcPort = dict()
packet_in_dstPort = dict()

sflow_url = r"http://192.168.203.156:8008/metric/192.168.203.148/json"

# 定时计算、输出数据量
# 1.计算packet-in数量
# 2.计算熵值分布，获取端口流出流量
# 3.判断是否超出阈值
# 4.
def _timer_func():

    log.info("-----P1 timer begins-----")
    global packet_in_counter
    global packet_in_srcIP, packet_in_dstIP, packet_in_srcPort, packet_in_dstPort

    imp.acquire_lock()

    log.info("packet-in count in 5s:" + str(packet_in_counter))

    # if packet_in_counter > 0:
    #     # 抛出事件
    #     core.Phase1.raiseEvent(TestEvent("packet_in_counter=%s" % packet_in_counter))

    # 1.计算熵值
    sip_entropy = calculate_entropy(packet_in_srcIP)
    dip_entropy = calculate_entropy(packet_in_dstIP)
    sport_entropy = calculate_entropy(packet_in_srcPort)
    dport_entropy = calculate_entropy(packet_in_dstPort)

    # 测试输出熵值

    # 2.sFlow-rt获取实时速率信息
    try:
        r = requests.get(sflow_url)
        decoded = json.loads(r.text)

        #     # 36是s7（122）  38是s8（124）
        # metrics = ["36.ifoutpkts", "36.ifoutoctets", "38.ifoutpkts", "38.ifoutoctets"]

        pkts_122 = decoded['36.ifoutpkts']
        bytes_122 = decoded['36.ifoutoctets']
        pkts_124 = decoded['38.ifoutpkts']
        bytes_124 = decoded['38.ifoutoctets']

        pkts_subnet5 = round(pkts_122 + pkts_124, 2)
        bytes_subnet5 = round(bytes_122 + bytes_124, 2)

        log.info("pkts_subnet5:%s" % pkts_subnet5)

    except Exception:
        pkts_subnet5 = 0
        bytes_subnet5 = 0

    # 3. 把熵值+速率信息组装tuple，输出日志
    ordered_dict = collections.OrderedDict()
    ordered_dict['sip'] = sip_entropy
    ordered_dict['dip'] = dip_entropy
    ordered_dict['sport'] = sport_entropy
    ordered_dict['dport'] = dport_entropy
    ordered_dict['pkt_num'] = packet_in_counter

    # 统计采样的数据
    # 现在的处理方法是获取发给122和124的包数量 + 发给1
    ordered_dict['pkts_subnet5'] = pkts_subnet5
    ordered_dict['bytes_subnet5'] = bytes_subnet5

    pktin_str = json.dumps(ordered_dict)
    with open(r"E://data/P1.txt", 'a+') as f:
        # 考虑启线程写
        f.write("".join(pktin_str+"\n"))

    log.info("sip:%s, dip:%s, sport:%s, dport:%s" % (sip_entropy, dip_entropy, sport_entropy, dport_entropy))
    log.info("sip:%s" % packet_in_srcIP)
    log.info("---------finish----------")

    # 4. 统计变量清零
    packet_in_counter = 0
    packet_in_srcIP.clear()
    packet_in_dstIP.clear()
    packet_in_srcPort.clear()
    packet_in_dstPort.clear()

    imp.release_lock()


class Phase1 (EventMixin):
    _eventMixin_events = set([TestEvent, P1Alert])  # 定义事件列表

    def __init__(self):
        EventMixin.__init__(self)
        core.pktinHandler.addListeners(self)  # 监听pktinHandler
        # print("Phase1 init")

    # 用于监听处理好了的packetIn
    def _handle_MaturePacketIn(self, maturePacketIn):
        # 时间窗口统计等等
        # log.info("receive mature packet in")
        global packet_in_counter

        imp.acquire_lock()

        packet_in_counter += 1
        update_dict(packet_in_srcIP, maturePacketIn.srcIP)
        update_dict(packet_in_dstIP, maturePacketIn.dstIP)
        # 这里port用
        update_dict(packet_in_srcPort, maturePacketIn.portSrc)
        update_dict(packet_in_dstPort, maturePacketIn.portDst)

        imp.release_lock()


def launch():
    from pox.lib.recoco import Timer
    core.registerNew(Phase1)

    global INTERVAL
    Timer(INTERVAL, _timer_func, recurring=True)
