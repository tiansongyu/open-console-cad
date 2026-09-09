"""加入空白学习卡带、双面 64 个金手指、内部 ROM 示意，以及变压器式适配器外壳与内部结构；不包含游戏 ROM 或封面素材。"""
from cadlib.megadrive import stage10

def build(model):
    return stage10(model)
