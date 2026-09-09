"""加入 64 个折弯弹片卡带触点、上部导向框、电源与音频电容和分区离散元件；保留卡带插入空间。"""
from cadlib.megadrive import stage05

def build(model):
    return stage05(model)
