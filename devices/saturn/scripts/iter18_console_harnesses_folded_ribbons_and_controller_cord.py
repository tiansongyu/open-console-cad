"""加入主机供电、光驱排线、指示灯、门检测和复位线束及屏蔽通道，补齐手柄九芯线、护线套和原始矩形插头；展示走线与线数不定义原厂电路。"""
from cadlib.saturn import stage18

def build(model):
    return stage18(model)
