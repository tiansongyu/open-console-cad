"""修正 GamePad 线束与螺柱、屏蔽罩和其他线束的间隙；加入 Basic 套装 HDMI 线、两端梯形金属插头、十九接点及带内孔的护线套。"""
from cadlib.wiiu import stage21

def build(model):
    return stage21(model)
