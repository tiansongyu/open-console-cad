"""补齐原版双手柄端口、绝缘载体与九位触点；将面板和按键文字投到实际曲面上，避免平面字片埋入斜面。接点尺寸为学习示意。"""
from cadlib.saturn import stage04

def build(model):
    return stage04(model)
