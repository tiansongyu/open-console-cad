"""加入初代特有的四个六接点 GameCube 手柄接口、两个十二接点存储卡槽及独立侧盖，补齐相对侧的进气孔。"""
from cadlib.wii import stage04

def build(model):
    return stage04(model)
