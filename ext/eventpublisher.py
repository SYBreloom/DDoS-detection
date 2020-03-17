# coding=utf-8

# Author: $￥
# @Time: 2019/9/5 16:30

from pox.core import core
from MyEventLib import MyEvent, MyEvent2
from pox.lib.revent.revent import EventMixin  # 发布事件需要继承自这个类

class eventPublisher(EventMixin):
    _eventMixin_events = set([MyEvent, MyEvent2])  # 定义事件列表

    def __init__(self):
        EventMixin.__init__(self)
        print "publisher init"


def launch():
    core.registerNew(eventPublisher)
