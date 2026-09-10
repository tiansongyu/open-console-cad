"""加入原版独立 CD 子系统板、SH-1 与 CD 控制封装、缓存和支承，补齐后部可换 CR2032 电池、备份复位键及双面卡槽触点；局部引脚与连接尺寸为学习近似。"""
from cadlib.saturn import stage07

def build(model):
    return stage07(model)
