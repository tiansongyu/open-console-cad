"""依据初代外壳系列 VA2 拆机照片布置主板、68000、Z80、YM2612、VDP、I/O 与存储器；内部尺寸及未标定芯片布局为学习近似。"""
from cadlib.megadrive import stage04

def build(model):
    return stage04(model)
