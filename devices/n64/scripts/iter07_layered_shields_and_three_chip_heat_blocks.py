"""补齐低矮电容与时钟件、上下屏蔽、CPU/RCP/内存三块导热金属块及折弯横梁，并加入十处独立散热紧固件和配合孔。"""
from cadlib.n64 import stage07

def build(model):
    return stage07(model)
