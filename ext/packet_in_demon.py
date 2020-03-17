# coding=utf-8

# Author: $￥
# @Time: 2019/8/2 14:48

from pox.core import core
import time
import collections
from pox.lib.revent.revent import EventMixin  # 发布事件需要继承自这个类
from pox.lib.revent.revent import Event  # 时间监听需要
import pox.lib.packet as pkt
from pox.lib.packet import dns
from MyEventLib import *
from pox.lib.addresses import IPAddr,IPAddr6,EthAddr
from pox.lib.addresses import IP_BROADCAST, IP_ANY
import collections
log = core.getLogger()


class pktinHandler(EventMixin):
    _eventMixin_events = set([MyEvent, MyEvent2, MaturePacketIn])  # 定义事件列表

    def __init__(self):
        # 父类初始化
        EventMixin.__init__(self)

        self.connections = set()  # 不确定需不需要留下
        core.openflow.addListeners(self)

    # 定义连接上switch以后的动作
    def _handle_ConnectionUp(self, event):
        log.debug("connection %s" % event.connection)
        self.connections.add(event.connection)
        # self.__handle_PacketIn(event.connection)

    # 定义接受packetIn的动作
    def _handle_PacketIn(self, event):
        packet = event.parsed
        sw_name = str(event.dpid) + "-" + str(event.port)

        # pkt-in 只获取5号交换机的信息，这里其实也可以转为在定义事件的时候，定义从哪个sw听到pkt-in
        if str(event.dpid) == '5':

            ether = packet.find('ethernet')
            if ether is None:
                print ('Ether none')
            else:
                # 提取ether层信息：source and destination MAC address ,packetLength
                ether_src = ether.src
                ether_dst = ether.dst
                ether_length = len(ether)
                if ether_dst.to_str() == dns.MDNS_ETH.to_str() or \
                        ether_dst.to_str() == dns.MDNS6_ETH.to_str() or \
                        ether_dst.to_str() == EthAddr('ff:ff:ff:ff:ff:ff'):
                    # 之前的方法写的是ether_dst.is_multicast?
                    # 过滤掉广播的帧
                    # print('exist?' + str(ether_dst))
                    pass
                elif ether.type == ether.IP_TYPE:
                    # 提取IP
                    ip_packet = ether.payload
                    ip_src = ip_packet.srcip
                    ip_dst = ip_packet.dstip  # 这里其实讲道理需要判断是不是0.0.0.0或者255.255.255.255

                    # 过滤广播的包
                    if ip_dst == IP_BROADCAST or ip_dst == IP_ANY:
                        pass
                    # 判断是不是发进区域里来的pkt-in，相对于发出去而言，好像可以用它提供的inNetwork函数，但是文档没有说明，懒得绕路
                    elif not str(ip_dst).startswith("192.168."):
                        pass
                    else:
                        # log.info(ether.payload)

                        port_src = ''
                        port_dst = ''
                        # 提取传输层信息，无论是TCP还是UDP（数据集里面的DNS 请求会用UDP）：source port and destination port
                        if ip_packet.protocol == pkt.ipv4.TCP_PROTOCOL:
                            tcp_packet = ip_packet.payload
                            port_src = tcp_packet.srcport
                            port_dst = tcp_packet.dstport
                        elif ip_packet.protocol == pkt.ipv4.UDP_PROTOCOL:
                            udp_packet = ip_packet.payload
                            port_src = udp_packet.srcport
                            port_dst = udp_packet.dstport

                        self.raiseEvent(MaturePacketIn(str(ip_src), str(ip_dst), str(port_src), str(port_dst)))


                    pass


def launch():

    core.registerNew(pktinHandler)
    # core.openflow.addListenerByName("PacketIn", _handle_packetin)
