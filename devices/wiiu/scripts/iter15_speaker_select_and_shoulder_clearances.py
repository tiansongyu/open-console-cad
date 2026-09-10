"""根据装配求交结果分开右扬声器与 SELECT 推杆，并同步调整扬声器开口；移开肩键小板，使其避让模拟摇杆电位器。"""
from cadlib.wiiu import stage15

def build(model):
    return stage15(model)
