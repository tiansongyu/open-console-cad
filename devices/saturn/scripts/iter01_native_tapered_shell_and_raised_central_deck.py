"""按 HST-3200 灰色初代照片建立独立上下空心壳、倾斜侧肩与原生多截面抬高中央台；260 × 230 × 83 mm 仅作为近似学习包络，家族规格依据另行注明。"""
from cadlib.saturn import stage01

def build(model):
    return stage01(model)
