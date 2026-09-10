"""调整盖板固定与手柄硅胶边界，补齐原版形式的日式电源线、八字端头、十接点 AV 转三 RCA 线及空白 12 cm 光盘，保留独立配件和组件编号。"""
from cadlib.saturn import stage19

def build(model):
    return stage19(model)
