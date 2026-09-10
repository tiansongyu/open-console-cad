"""加入两排 50 位卡带连接器、36 位内存接口及原始 Jumper Pak，分别表示弹片、终端板、金手指和电阻网络，避免混用后期扩展内存模块。"""
from cadlib.n64 import stage06

def build(model):
    return stage06(model)
