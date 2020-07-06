# coding=utf-8

# Author: $￥
# @Time: 2019/9/16 20:01
# 单纯为了测试准确率写的，没有对于EventMixin的获取和处理
# 去除了所有事件的传递

from pox.core import core
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
import imp
import time
from EntropyHelper import calculate_entropy, update_dict
import collections
import json

INTERVAL = 3

log = core.getLogger()
dict_stats = {}


def _timer_func():
    for connection in core.openflow._connections.values():

        dpid_str = dpidToStr(connection.dpid)

        # todo 这里需要修改，做准确率判断的话监听s7的h122，
        # todo 否则根据P1Alert报告的数据，从P1Alert.switch_dpid  和 P1Alert.host_id 处理对于的监控信息

        # 只发dpid 07的edge switch
        if dpid_str == "00-00-00-00-00-07":
            connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
            # connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))


class Phase2:
    def __init__(self):
        core.openflow.addListeners(self)

    # 函数来自于pox.forwarding.flow_stats_10mbps
    def _handle_FlowStatsReceived(self, flow_stats_received):
        log.info("-------------receive stats----------------")

        imp.acquire_lock()
        now_time = time.strftime("%H:%M:%S", time.localtime())
        imp.release_lock()

        new_dict = {}  # <flow: stats>的快照字典,保存这次存下来的统计快照
        record = []  # 和上次快照比较，计算得到的速率

        # stats结构体解析
        for f in flow_stats_received.stats:  # f的结构体: libopenflow_01.ofp_flow_stats

            # IP UDP/TCP
            if not(f.match.dl_type == 0x800 and (f.match.nw_proto == 17 or f.match.nw_proto == 6) and \
                    f.match.nw_dst == "192.168.5.122"):  # 锁定了监听的目标主机
                # 打出来看的话应该是arp(0x0806) 或者是 LLDP(0x88CC)
                pass
            else:
                # flow的标识
                ip_src = str(f.match.nw_src)
                ip_dst = f.match.nw_dst
                tp_src = f.match.tp_src
                tp_dst = f.match.tp_dst
                flow_protocol = f.match.nw_proto

                # 特征信息
                flow_byte_count = f.byte_count
                flow_packet_count = f.packet_count

                # debug 查看match的flow
                # log.info("ip_src:%s, ip_dst:%s, tp_src:%s, tp_dst:%s, protocol:%s",
                #          ip_src, ip_dst, tp_src, tp_dst, flow_protocol)
                flow_id = FlowId(ip_src, tp_src, ip_dst, tp_dst, flow_protocol)

                global dict_stats

                # 对于在之前存在快照的flow 计算速率
                if flow_id in dict_stats.keys():
                    old_flow_count = dict_stats.get(flow_id)
                    byte_count = float(flow_byte_count - old_flow_count.byte_count)
                    pkt_count = float(flow_packet_count - old_flow_count.packet_count)

                    # 只纪录活跃的flow，同时记录差值
                    if pkt_count > 0 and byte_count > 0:
                        record.append((now_time, flow_id, round(byte_count, 2), round(pkt_count, 2)))
                else:
                    # 上一次的dict里面没有这个流
                    # LFA里面的做法是不处理这个新的流，这里P2检测的时候因为流比较少还是拿进来处理了,计算实时流量
                    # log.info("this flow is not in %ss before" % INTERVAL)

                    byte_count = float(flow_byte_count)
                    pkt_count = float(flow_packet_count)

                    if pkt_count > 0 and byte_count > 0:
                        record.append((now_time, flow_id, round(byte_count, 2), round(pkt_count, 2)))

                # 更新本次的map
                flow_count = FlowCount(flow_byte_count, flow_packet_count)
                new_dict.setdefault(flow_id, flow_count)

                # log.info("byte_count:%s ; pkt_count:%s ", f.byte_count, f.packet_count)

        # 计算得到的实时速率的总和以及熵值
        byte_sum = 0
        pkt_sum = 0

        byte_count_dict = {}  # 统计srcIP发给victim的byte增量
        pkt_count_dict = {}  # 统计srcIP发给victim的pkt增量
        active_src_ip = []
        active_src_port = []

        # 从速率计算的dict里面计算总和速率、活跃的数量、熵值等
        for i in record:

            flow_id = i[1]
            byte_count = i[2]
            pkt_count = i[3]

            byte_sum += byte_count
            pkt_sum += pkt_count
            # 因为前面获取ststas的时候已经锁定了监听的目标主机，只需要统计发给它的src就可以了
            # 但是dst_port可能不一样，我把它按照ip算了，把port汇聚起来了只管dst_port
            # ip考虑到攻击用的port 就还是保留port了

            if flow_id.get_ip_src() not in active_src_ip:
                active_src_ip.append(flow_id.get_ip_src())

            src_addr = str(flow_id.get_ip_src()) + " " + str(flow_id.get_src_port())
            if src_addr not in active_src_port:
                active_src_port.append(src_addr)

            update_dict(byte_count_dict, src_addr, value=byte_count)
            update_dict(pkt_count_dict, src_addr, value=pkt_count)

        # 日志debug 输出计算的速率总量，和ip、port数量dict
        # log.info(byte_count_dict)
        # log.info(pkt_count_dict)
        # log.info(active_src_ip)
        # log.info(active_src_port)

        byte_rate = round(float(byte_sum)/INTERVAL, 2)
        pkt_rate = round(float(pkt_sum)/INTERVAL, 2)

        # 复用前面的函数，计算熵值
        byte_count_entropy = calculate_entropy(byte_count_dict)
        pkt_count_entropy = calculate_entropy(pkt_count_dict)

        # 日志debug 输出计算的feature结果
        # log.info("byte_rate:%s; pkt_rate:%s" % (byte_rate, pkt_rate))
        # log.info("active srcIP:%s ; active srcPort:%s" % (len(active_src_ip), len(active_src_port)))
        # log.info("byte_rate_entropy:%s; pkt_rate_entropy:%s" % (byte_count_entropy, pkt_count_entropy))

        if byte_sum > 0 and pkt_sum > 0:
            # 加了一个判断，只有发给122的总速率大于0的时候才写文件
            # 输出速率 1.速率 2.活跃的src 3.byte_entropy
            ordered_dict = collections.OrderedDict()
            ordered_dict['byte_rate'] = byte_rate
            ordered_dict['pkt_rate'] = pkt_rate
            ordered_dict['active_src_ip'] = len(active_src_ip)
            ordered_dict['active_src_port'] = len(active_src_port)
            ordered_dict['byte_count_entropy'] = byte_count_entropy
            ordered_dict['pkt_count_entropy'] = pkt_count_entropy

            feature_json = json.dumps(ordered_dict)

            with open(r"E://data/P2.txt", 'a+') as f:
                # 考虑启线程写
                log.info('write over')
                f.write("".join(feature_json + "\n"))

        record = []  # 清空list
        dict_stats = new_dict.copy()  # 更新dict
        log.info("----------------finish--------------------")
        # log.info(dict_tmp)


class FlowId(object):
    # 定义flow结构，用 <src_ip:src_port  ->  dst_ip:dst_port protocol> 标识一个flow
    def __init__(self, ip_src, src_port, ip_dst, dst_port, protocol):
        self._ip_src = ip_src
        self._src_port = src_port
        self._ip_dst = ip_dst
        self._dst_port = dst_port
        self._protocol = protocol

    def get_ip_src(self):
        return self._ip_src

    def get_src_port(self):
        return self._src_port

    def get_ip_dst(self):
        return self._ip_dst

    def get_dst_port(self):
        return self._dst_port

    def __str__(self):
        return "<%s:%s %s:%s %s>" % (self._ip_src, self._src_port, self._ip_dst, self._dst_port, self._protocol)

    def __eq__(self, other):
        return str(self).__eq__(str(other))  # 偷懒版

    def __hash__(self):
        return hash(str(self))


class FlowCount(object):
    def __init__(self, byte_count, packet_count):
        self.byte_count = byte_count
        self.packet_count = packet_count

    def __str__(self):
        return "Byte: %s; Packet: %s" % (self.byte_count, self.D)


def launch():
    from pox.lib.recoco import Timer
    core.registerNew(Phase2)

    # 如果我需要做实时的，这里的timer_func应该就需要根据事件的触发进行响应；否则为了检测率可以直接就是一直监控s7，不听事件
    global INTERVAL
    Timer(INTERVAL, _timer_func, recurring=True)
