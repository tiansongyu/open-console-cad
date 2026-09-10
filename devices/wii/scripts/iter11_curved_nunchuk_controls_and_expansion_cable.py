"""加入原生贝塞尔轮廓的 Nunchuk 曲面外壳、模拟摇杆、C/Z 键、控制板与扩展线；同时按干涉报告调整主机外壳支柱与无线接口周边间隙。"""
from cadlib.wii import stage11

def build(model):
    return stage11(model)
