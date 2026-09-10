"""补齐双 USB、十六位 Multi AV、感应条和直流电源接口的独立触点及背部排气格栅，同时细化前面板电源/退盘符号。"""
from cadlib.wii import stage03

def build(model):
    return stage03(model)
