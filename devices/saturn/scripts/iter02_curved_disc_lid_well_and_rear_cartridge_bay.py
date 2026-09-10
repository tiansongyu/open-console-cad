"""加入带弧形前缘的原生光驱盖、深光盘仓与光头通道、后部卡槽衬框及防尘门，补齐灰色初代的顶盖文字和深色弧形装饰。"""
from cadlib.saturn import stage02

def build(model):
    return stage02(model)
