"""补齐主板背面的三块独立无线模块、屏蔽罩、微型同轴端口和兼容模式存储器，并调整两枚器件以消除与电容的干涉。"""
from cadlib.wiiu import stage05

def build(model):
    return stage05(model)
