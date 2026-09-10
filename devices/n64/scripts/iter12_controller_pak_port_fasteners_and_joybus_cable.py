"""补齐 32 位手柄扩展接口、九处主壳及两处接口固定、三芯线和专用插头，并加入编码小板与六芯模块线束。"""
from cadlib.n64 import stage12

def build(model):
    return stage12(model)
