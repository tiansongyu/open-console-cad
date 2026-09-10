"""补齐上壳八字电源座、下壳 AV 与通信接口、独立后部电池扩展盖，以及侧面和底部通风槽；接口触点与局部尺寸保留学习近似说明。"""
from cadlib.saturn import stage05

def build(model):
    return stage05(model)
