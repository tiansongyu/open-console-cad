"""移开主板电源插座以避让无源器件，并调整光驱支承孔；采用独立字形间距修复微小 CAD 文字的自交，对全部已建组件执行严格实体检查。"""
from cadlib.saturn import stage08

def build(model):
    return stage08(model)
