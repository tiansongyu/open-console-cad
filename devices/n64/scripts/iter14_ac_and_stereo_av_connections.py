"""加入固定 AC 线及日式插头、Multi Out 转立体声三 RCA 线，修正六芯回路线避免交叉，并补齐卡带屏蔽固定和存储卡插入舌部。"""
from cadlib.n64 import stage14

def build(model):
    return stage14(model)
