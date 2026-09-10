"""加入 Basic 套装的 WUP-002 主机电源和 WUP-011 GamePad 电源，分别绘制空心壳、线缆、日式插头、专用双接点端头及内部结构示意；适配器局部尺寸为照片近似。"""
from cadlib.wiiu import stage20

def build(model):
    return stage20(model)
