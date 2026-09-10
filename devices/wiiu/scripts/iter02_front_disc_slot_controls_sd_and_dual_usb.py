"""加入吸入式光盘槽、电源与退盘控制、外露红色同步键，以及独立前门内的九接点 SD 卡座与双 USB 接口。"""
from cadlib.wiiu import stage02

def build(model):
    return stage02(model)
