"""加入显示、双侧按键、底部控制与 NFC 软排线，补齐电池、立体声扬声器、麦克风和无线天线连接；保留独立组件及显示支架通道，线数和局部路径为示意。"""
from cadlib.wiiu import stage18

def build(model):
    return stage18(model)
