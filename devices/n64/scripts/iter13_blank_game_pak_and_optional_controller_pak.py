"""加入弧顶空白卡带、双面金手指、金属屏蔽和可选 Controller Pak，补齐存储卡电池示意，并修正摇杆安装页和扩展接口的插入空间。"""
from cadlib.n64 import stage13

def build(model):
    return stage13(model)
