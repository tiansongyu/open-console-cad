"""加入四支白色长支座、独立光驱控制板、主轴与定位台、双导轨光头、螺旋进给件和电机，保留机架、固定件与光盘仓的装配间隙。"""
from cadlib.saturn import stage09

def build(model):
    return stage09(model)
