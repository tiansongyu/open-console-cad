"""加入真实贯穿的吸入式光盘槽、蓝色导光件、独立电源与重置/退盘键、前门、九接点 SD 卡座及红色同步键。"""
from cadlib.wii import stage02

def build(model):
    return stage02(model)
