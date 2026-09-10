"""移开第二根电源开关线与第一根下降弯管的局部相交，保留端头位置及相邻板件间隙。"""
from cadlib.saturn import stage22

def build(model):
    return stage22(model)
