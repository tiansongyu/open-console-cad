"""保留曲面与开孔的有效分段边界，合并相接的存储器文字实体，并将四角固定柱完全修整到拱形外表面以下；全部物理组件执行严格 BRep 检查。"""
from cadlib.n64 import stage15

def build(model):
    return stage15(model)
