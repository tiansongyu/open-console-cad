"""补齐手柄线束端子、卡带固定柱、原始 DIN 转双 RCA 单声道视频线与外接 DC 线，并保留插头、导体和护套的组件身份。"""
from cadlib.megadrive import stage12

def build(model):
    return stage12(model)
