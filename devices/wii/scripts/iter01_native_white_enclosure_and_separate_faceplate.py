"""建立初代白色 RVL-001 的原生草图、拉伸与圆角外壳，独立前面板及四个横放脚垫；按 157 × 215.4 × 44 mm 横放坐标建模。"""
from cadlib.wii import stage01

def build(model):
    return stage01(model)
