"""加入原始 Multi Out 十二接点接口、后右侧可拆电源模块、六位电源连接器和两侧通风孔，保留电源模块上下空心壳。"""
from cadlib.n64 import stage04

def build(model):
    return stage04(model)
