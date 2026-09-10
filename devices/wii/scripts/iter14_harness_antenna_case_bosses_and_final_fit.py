"""补齐光驱排线与供电线、前灯和风扇线束、两条 Wi-Fi 天线线及遥控器/双节棍三翼螺钉，修正小板与接点间隙，并打开主机前缘的光盘与走线通道。"""
from cadlib.wii import stage14

def build(model):
    return stage14(model)
