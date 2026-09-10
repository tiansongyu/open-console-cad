"""加入原版电源适配器的结构示意、日式电源插头、双芯直流插头、十六位 AV 转三 RCA 线，以及不含游戏数据的 12 cm 与 8 cm 空白光盘。"""
from cadlib.wii import stage13

def build(model):
    return stage13(model)
