"""加入四个圆形灰色手柄接口、三路触点与定位圆点，补齐正面徽标和独立电源指示灯，保留上下壳的接口开孔历史。"""
from cadlib.n64 import stage02

def build(model):
    return stage02(model)
