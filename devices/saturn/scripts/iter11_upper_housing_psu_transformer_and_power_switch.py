"""加入初代 HST-3200 的上壳电源板、变压器、滤波与散热器件、支承框和锁定电源开关，保留独立市电端头与线束；内部器件尺寸与电路为结构学习示意。"""
from cadlib.saturn import stage11

def build(model):
    return stage11(model)
