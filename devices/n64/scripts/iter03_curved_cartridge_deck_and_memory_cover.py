"""加入随拱形上盖弯曲的卡带台和内存扩展盖，补齐对开灰色防尘门、弧形通风槽、椭圆 POWER/RESET 按键及顶部标识。"""
from cadlib.n64 import stage03

def build(model):
    return stage03(model)
