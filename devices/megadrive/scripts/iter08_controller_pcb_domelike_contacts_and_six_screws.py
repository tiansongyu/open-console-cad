"""补齐手柄电路板、八组碳膜触点与硅胶按键、复用器示意和六处后壳固定；内部组件可按装配分组单独查看。"""
from cadlib.megadrive import stage08

def build(model):
    return stage08(model)
