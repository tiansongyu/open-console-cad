"""加入日版卡带口和防尘门、耳机音量滑块、卡带锁联动电源、蓝色 RESET、16-BIT 标识及左侧贯穿散热槽。"""
from cadlib.megadrive import stage02

def build(model):
    return stage02(model)
