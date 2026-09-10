"""加入上下屏蔽板、主板和光驱支柱及机壳螺钉；修正无线接口罩和风道底部的实际装配间隙，避免螺柱超出圆角外形。"""
from cadlib.wiiu import stage08

def build(model):
    return stage08(model)
