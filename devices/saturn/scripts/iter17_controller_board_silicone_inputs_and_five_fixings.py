"""补齐原版手柄的电路板、三组硅胶膜、碳膜接点、I/O 器件、肩键微动开关与五处外壳固定；同时完善主机灯板螺孔及卡槽防尘门轴孔。"""
from cadlib.saturn import stage17

def build(model):
    return stage17(model)
