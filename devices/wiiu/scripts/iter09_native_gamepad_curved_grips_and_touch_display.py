"""建立 GamePad 原生曲面前后壳、空心握柄和 6.2 英寸显示层，保留金属背板、LCD 支承、触摸层和黑色细边框的独立组件。"""
from cadlib.wiiu import stage09

def build(model):
    return stage09(model)
