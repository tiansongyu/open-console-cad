"""建立 SJ-3500 原生曲线剖面上下壳，加入浮动圆盘十字键、斜列 ABC 三键和蓝色 START；保留初代三键手柄轮廓。"""
from cadlib.megadrive import stage06

def build(model):
    return stage06(model)
