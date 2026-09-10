"""以共用传送机构原语建立 Wii U 吸入式光驱，重新确定机架尺寸、上盖加强筋和安装点，保留主轴、滚轮、齿轮及导轨光头。"""
from cadlib.wiiu import stage07

def build(model):
    return stage07(model)
