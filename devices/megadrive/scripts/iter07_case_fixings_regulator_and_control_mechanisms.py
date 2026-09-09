"""补齐六处壳体紧固、支柱与主板通孔，加入折弯散热片、稳压器、音量滑块及电源/RESET 内部传动，并修正防尘门轴的运行间隙。"""
from cadlib.megadrive import stage07

def build(model):
    return stage07(model)
