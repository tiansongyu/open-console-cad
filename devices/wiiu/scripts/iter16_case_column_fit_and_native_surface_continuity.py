"""依据全装配求交移动下部螺柱并补齐按键板和支承框的通孔；保留壳体分段曲面以避免自动合并损坏曲线，并执行全部组件严格实体检查。"""
from cadlib.wiiu import stage16

def build(model):
    return stage16(model)
