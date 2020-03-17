# coding=utf-8

# Author: $￥
# @Time: 2019/9/5 16:33

from pox.core import core
from eventpublisher import eventPublisher


class eventListener ():
    def __init__(self):
        core.eventPublisher.addListeners(self)
        self.listenTo()
        print("eventlistner init")

    def _handle_MyEvent(self, event):
        print("handle my event")

    def _handle_MyEvent2(self, event):
        print("handle my event2")

def launch():
    core.registerNew(eventListener)

