"""依据全装配求交结果移动双节棍前固定点、避让光驱支柱并分开前灯线束的转弯高度，逐一执行全部组件的严格 BRep 检查。"""
from cadlib.wii import stage15

def build(model):
    return stage15(model)
