"""建立 260 × 190 mm 整体范围的上下空心壳、四角低台与脚垫，使用可编辑圆柱曲面生成初代 N64 的横向拱形顶盖。"""
from cadlib.n64 import stage01

def build(model):
    return stage01(model)
