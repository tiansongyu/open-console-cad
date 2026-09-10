"""加入原生螺旋回中弹簧、双向支承、开槽光学编码轮与独立光电元件，并补齐背部 Z 键、推杆和专用小板；机构尺寸为学习近似。"""
from cadlib.n64 import stage11

def build(model):
    return stage11(model)
