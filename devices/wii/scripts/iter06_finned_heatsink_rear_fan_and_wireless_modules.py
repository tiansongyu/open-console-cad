"""加入共用铝制鳍片散热器、七叶后排风扇、独立 Wi-Fi 与蓝牙模块及屏蔽罩，留出后部接口与光驱的装配空间。"""
from cadlib.wii import stage06

def build(model):
    return stage06(model)
