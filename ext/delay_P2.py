# coding=utf-8

# Author: $￥
# @Time: 2019/10/7 13:39

from pox.core import core
from pox.lib.revent.revent import EventMixin
from MyEventLib import TestEvent, P2Alert
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
import imp
import time
from EntropyHelper import calculate_entropy, update_dict
from pox.lib.recoco import Timer
import SOM_validate
import SVM_validate

INTERVAL = 3

log = core.getLogger()
dict_stats = {}

request_trigger = False  # True表示正在发request,此使不能发request,可以收 statstics ; False 表示可以发request
timer_fun_counter = 0


class Phase2 (EventMixin):
    _eventMixin_events = set([P2Alert])  # 定义事件列表

    def __init__(self):
        EventMixin.__init__(self)
        core.Phase1.addListeners(self)  # 监听phase1 是否进入phase2的检测
        core.openflow.addListeners(self)  # 监听openflow的stats_信息

    def send_stats_request(self, switch_dpid):
        if request_trigger:

            for connection in core.openflow._connections.values():
                dpid_str = dpidToStr(connection.dpid)

                # 根据P1Alert报告的数据，从P1Alert.switch_dpid 处理需要监控sw
                if dpid_str == switch_dpid:
                    # log.info("send request")
                    # 给每个connection的sw发送request 可以加if判断发送哪个
                    connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
                    # connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))

    def timer_func(self, switch_dpid):
        global timer_fun_counter, request_trigger
        timer_fun_counter += 1

        if timer_fun_counter > 3:
            # 每次Phase2 $￥只允许发3次stats_request
            request_trigger = False
            timer_fun_counter = 0
            return False

        if request_trigger:

            for connection in core.openflow._connections.values():
                dpid_str = dpidToStr(connection.dpid)

                # 根据P1Alert报告的数据，从P1Alert.switch_dpid 处理需要监控sw
                if dpid_str == switch_dpid:
                    # log.info("send request")
                    # 给每个connection的sw发送request 可以加if判断发送哪个
                    connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
                    # connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))

    def _handle_P1Alert(self, P1Alert):
        switch_dpid = P1Alert.switch_dpid
        self.host_id = P1Alert.host_id
        imp.acquire_lock()
        now_time = time.strftime("%H:%M:%S", time.localtime())
        imp.release_lock()

        log.info("sy receive P1Alert %s" % now_time)

        global INTERVAL, request_trigger

        if not request_trigger:
            # 防止重复使用timer_func   只有当trigger 为 False的时候允许进入
            request_trigger = True

            # 在周期性执行core.Phase2.timer_func前先发一条
            self.send_stats_request(switch_dpid)

            Timer(INTERVAL, core.Phase2.timer_func, recurring=True, args=(switch_dpid,))
        pass

    def _handle_FlowStatsReceived(self, flow_stats_received):
        log.info("-------------receive stats----------------")
        imp.acquire_lock()
        now_time = time.strftime("%H:%M:%S", time.localtime())
        imp.release_lock()
        log.info(now_time)

        imp.acquire_lock()
        now_time = time.strftime("%H:%M:%S", time.localtime())
        imp.release_lock()

        new_dict = {}  # <flow: stats>的快照字典,保存这次存下来的统计快照
        record = []  # 和上次快照比较，计算得到的速率

        # stats结构体解析
        for f in flow_stats_received.stats:  # f的结构体: libopenflow_01.ofp_flow_stats

            # IP UDP/TCP
            if not(f.match.dl_type == 0x800 and (f.match.nw_proto == 17 or f.match.nw_proto == 6) and \
                    f.match.nw_dst == self.host_id):  # todo 测试potential victim 锁定了监听的目标主机
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

        feature_list = (byte_rate, pkt_rate, len(active_src_ip), len(active_src_port),
                        byte_count_entropy, pkt_count_entropy)

        if len(dict_stats) == 0:
            # todo 测试
            log.info("dict empty test log")
        if len(dict_stats) > 0:
            # 只有上次的dict快照里面不空，才能算出准确的速率
            # label = SVM_validate.P2_validate(feature_list)
            label = SOM_validate.P2_validate(feature_list)
            log.info(label)
            print(label == 1)
            if label == 1:
                # verify attack
                self.raiseEvent(P2Alert(msg="$￥ detect"))
                global request_trigger

            else:
                log.info("P2 no attack")

            # todo 撤销timer_func后面的查询

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
    core.registerNew(Phase2)
