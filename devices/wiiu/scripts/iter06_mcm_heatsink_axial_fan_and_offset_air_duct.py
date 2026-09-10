"""加入多芯片封装的共用鳍片散热器、后部轴流风扇及原生剖面放样风道，保持散热层与外壳、端口和主板分离。"""
from cadlib.wiiu import stage06

def build(model):
    return stage06(model)
