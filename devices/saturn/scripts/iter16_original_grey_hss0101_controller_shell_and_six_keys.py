"""建立原版灰色 HSS-0101 手柄的原生曲线前后壳、圆盘十字键、黑色 ABC、蓝色 XYZ / START 和肩键，并补齐主机前部锁扣的光盘仓避让。"""
from cadlib.saturn import stage16

def build(model):
    return stage16(model)
