"""加入上下屏蔽板、通风与维修开口、手柄端口压条、上下壳螺柱和主板承托，保留螺钉、橡胶脚垫及板件的独立避让。"""
from cadlib.saturn import stage12

def build(model):
    return stage12(model)
