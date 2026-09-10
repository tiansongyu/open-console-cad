"""加入光驱盖原生轴耳、钢轴、回位弹簧、扇形齿轮与小齿轮及金属支架，保留屋面与轴承间隙；机构用于结构观察，不代表经过验证的运动仿真。"""
from cadlib.saturn import stage13

def build(model):
    return stage13(model)
