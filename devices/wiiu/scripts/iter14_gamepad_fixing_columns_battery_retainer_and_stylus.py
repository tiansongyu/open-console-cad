"""补齐 GamePad 外壳和主板固定点、电池盖螺钉与内部承托边框，并加入独立 WUP-015 触控笔学习模型。"""
from cadlib.wiiu import stage14

def build(model):
    return stage14(model)
