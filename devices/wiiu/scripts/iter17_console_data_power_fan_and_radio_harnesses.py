"""加入主机光驱数据软排线、独立供电导线、后排风扇线束与三组无线模块天线线，并在屏蔽板和无线小板保留走线通道；接点数量与局部走线为学习近似。"""
from cadlib.wiiu import stage17

def build(model):
    return stage17(model)
