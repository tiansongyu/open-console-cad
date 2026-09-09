"""加入精确圆弧扫掠的手柄线、九芯内部导线、空心护套与母头插头，补齐日版红色电源环带，并调整深色外壳的显示明度。"""
from cadlib.megadrive import stage09

def build(model):
    return stage09(model)
