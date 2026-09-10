"""加入参考 NUS-CPU-04 的主板、CPU/RCP、两片 RDRAM 及音视频和接口封装，补齐手柄接口穿板引脚，并让后部电源模块保持在拱形顶盖下方。"""
from cadlib.n64 import stage05

def build(model):
    return stage05(model)
