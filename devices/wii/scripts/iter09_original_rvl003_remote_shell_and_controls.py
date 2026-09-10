"""建立原版 RVL-003 遥控器的曲面后壳、正面按键、红外窗口、扬声器孔、四个指示灯、背部 B 键和六接点扩展接口，不加入 MotionPlus 外形。"""
from cadlib.wii import stage09

def build(model):
    return stage09(model)
