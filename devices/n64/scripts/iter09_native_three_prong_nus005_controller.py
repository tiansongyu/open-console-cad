"""建立初代 NUS-005 三叉曲线手柄上下壳，加入黑色十字键、红色 START、蓝 A 绿 B、四颗黄色 C 键、八角摇杆导向和肩键。"""
from cadlib.n64 import stage09

def build(model):
    return stage09(model)
