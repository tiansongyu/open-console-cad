"""依据装配检查为固定轴承开出盖板内部避让，降低齿轮支架和固定件，并调整光盘仓角部的支承间隙，保持外表面轮廓。"""
from cadlib.saturn import stage15

def build(model):
    return stage15(model)
