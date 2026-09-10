"""加入 L/R 与 ZL/ZR、可拆电池盖、音量滑块、耳机与充电端口、底部扩展口及充电触点，同时完善主机螺钉和风道的避让。"""
from cadlib.wiiu import stage11

def build(model):
    return stage11(model)
