"""补齐背面 HDMI 十九接点、AV 十六接点、感应条与供电口，以及堆叠双 USB、三列排风格栅和两侧通风槽。"""
from cadlib.wiiu import stage03

def build(model):
    return stage03(model)
