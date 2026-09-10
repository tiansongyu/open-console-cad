"""补齐遥控器控制板、红外相机、三轴加速度计、扬声器、偏心振动机构、两节 AA 电池及弹簧触点，加入按键导电接点和 B 键小板。"""
from cadlib.wii import stage10

def build(model):
    return stage10(model)
