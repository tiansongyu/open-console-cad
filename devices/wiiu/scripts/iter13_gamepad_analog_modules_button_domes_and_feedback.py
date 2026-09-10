"""加入双模拟摇杆的回中弹簧、支承和电位器、按键硅胶与推杆、肩键小板及偏心振动机构，保留可独立查看的机械和电子组件。"""
from cadlib.wiiu import stage13

def build(model):
    return stage13(model)
