"""补齐 GamePad 主板、无线和 NFC 模块、镂空显示支架、原版 1500 mAh 电池、独立按键板、相机、麦克风与立体声扬声器。"""
from cadlib.wiiu import stage12

def build(model):
    return stage12(model)
