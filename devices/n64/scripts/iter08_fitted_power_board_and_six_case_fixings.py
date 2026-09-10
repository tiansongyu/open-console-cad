"""将可拆电源模块收进后角支柱以内，补齐模块内部变压器示意、六处机壳固定及六处主板支承，并修正卡座安装片和板件避让。"""
from cadlib.n64 import stage08

def build(model):
    return stage08(model)
