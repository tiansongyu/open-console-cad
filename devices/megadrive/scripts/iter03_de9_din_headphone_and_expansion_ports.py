"""加入两只前面 DE-9 手柄接口、后扩展 DE-9、八针 DIN AV、DC 输入、前耳机口及右侧扩展盖；接口触点独立建模。"""
from cadlib.megadrive import stage03

def build(model):
    return stage03(model)
