"""补齐双摇杆、ABXY、十字键、START/SELECT、HOME 蓝色环、TV 和电源控制，加入前摄像头、红外窗口、NFC 标记及立体声开口。"""
from cadlib.wiiu import stage10

def build(model):
    return stage10(model)
