"""加入 Basic 主板、CPU/GPU 多芯片载板、四片 DDR3L 与 8 GB eMMC 封装，补齐视频、系统及分区供电器件；内部电路布置明确作为学习近似。"""
from cadlib.wiiu import stage04

def build(model):
    return stage04(model)
