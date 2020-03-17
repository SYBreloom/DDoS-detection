# coding=utf-8

# Author: $￥
# @Time: 2019/8/2 10:53
from pox.core import core
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *

INTERVAL = 5

log = core.getLogger()


def _timer_func():

    for connection in core.openflow._connections.values():

        dpid_str = dpidToStr(connection.dpid)

        # 给每个connection的sw发送request 可以加if判断发送哪个
        connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
        connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))

        # log.debug("")
        # todo 处理流信息

def _handle_port_stats_received(event):
    stats = flow_stats_to_list(event.stats)
    log.debug("FlowStatsReceived from %s: %s",
              dpidToStr(event.connection.dpid), stats)


def _handle_flow_stats_received(event):
    # stats = flow_stats_to_list(event.stats)
    # log.debug("FlowStatsReceived from %s: %s", dpidToStr(event.connection.dpid), stats)

    for flow in event.stats:
        if flow.match.dl_type == 0x800:
            byte_count = flow.byte_count
            packet_count = float.packet_count




def launch ():
    from pox.lib.recoco import Timer

    global INTERVAL

    # 让_handle_flow_stats_received函数监听FlowStatsReceived事件
    core.openflow.addListenerByName("FlowStatsReceived", _handle_flow_stats_received)
    # 让_handle_port_stats_received函数监听PortStatsReceived事件
    core.openflow.addListenerByName("PortStatsReceived", _handle_port_stats_received)

    # timer set to execute every five seconds
    Timer(INTERVAL, _timer_func, recurring=True)
