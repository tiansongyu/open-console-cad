"""依据 MAIN VA0.5 拆解布局建立主板、双 SH-2、两组图形处理器、SCU、音频处理、系统管理与分区存储，并加入电容、时钟、无源件与线束插座；引脚和电路布局为学习近似。"""
from cadlib.saturn import stage06

def build(model):
    return stage06(model)
