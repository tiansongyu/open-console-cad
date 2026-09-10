"""沿原生顶壳曲面分出深色控制面板，加入蓝色椭圆 POWER / RESET、中央 OPEN 键及双指示灯；按钮保留独立实体和外壳开孔。"""
from cadlib.saturn import stage03

def build(model):
    return stage03(model)
