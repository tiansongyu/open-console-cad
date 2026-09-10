"""加入手柄主板、十一组硅胶和碳膜接点、按钮传动柱及黄色方向标识，同时修正主机中心支柱、离散元件和横梁配合，并收紧肩键外形。"""
from cadlib.n64 import stage10

def build(model):
    return stage10(model)
