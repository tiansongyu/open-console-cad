"""按 172 × 268.5 × 46 mm 塑料主体建立原生圆角截面、长向拉伸、空心壳及上下分件，保留独立前面板和外伸脚垫。"""
from cadlib.wiiu import stage01

def build(model):
    return stage01(model)
