"""建立吸入式光驱的底架、双滚轮、齿轮、主轴与压盘件，并加入双导轨光头、螺旋进给丝杆和独立光驱控制板。"""
from cadlib.wii import stage07

def build(model):
    return stage07(model)
