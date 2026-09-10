"""补齐上下屏蔽板、主板与光驱支柱和机壳螺钉；通过主板后缘缺口及无线板位置调整消除风扇与支柱干涉。"""
from cadlib.wii import stage08

def build(model):
    return stage08(model)
