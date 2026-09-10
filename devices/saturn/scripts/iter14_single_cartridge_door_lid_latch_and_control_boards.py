"""按初代拆解修正整片卡槽防尘门，加入轴销与回位弹簧；补齐光驱盖锁扣、开盖导向、门检测开关、复位键及分立指示灯板和导光件。"""
from cadlib.saturn import stage14

def build(model):
    return stage14(model)
