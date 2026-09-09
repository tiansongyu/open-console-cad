"""依据整套求交检查收窄焊接端子、移开 DC 插头展示位置，并在 AV 分线护套中加工独立走线孔；所有线缆扫掠通过严格实体检查。"""
from cadlib.megadrive import stage13

def build(model):
    return stage13(model)
