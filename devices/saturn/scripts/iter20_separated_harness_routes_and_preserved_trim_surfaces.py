"""按装配求交分开灯板、门检测、复位和电源开关线束，调整相应通孔，并保留卡槽衬框和上壳的原始修剪曲面；全部已建组件执行严格实体检查。"""
from cadlib.saturn import stage20

def build(model):
    return stage20(model)
