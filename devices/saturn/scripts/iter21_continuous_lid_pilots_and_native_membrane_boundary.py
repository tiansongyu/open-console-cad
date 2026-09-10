"""贯通铰链支承与支架固定孔，采用原生求交限制硅胶膜边界，使后续重算仍保留真实间隙，并复查全部组件的严格实体有效性。"""
from cadlib.saturn import stage21

def build(model):
    return stage21(model)
