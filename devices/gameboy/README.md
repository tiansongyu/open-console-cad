# Nintendo Game Boy · DMG-01

[整机 3D](https://tiansongyu.github.io/open-console-cad/?device=gameboy&view=assembled#viewer) · [内部结构](https://tiansongyu.github.io/open-console-cad/?device=gameboy&view=internal#viewer) · [四节 AA 电池](https://tiansongyu.github.io/open-console-cad/?device=gameboy&view=battery#viewer) · [空白卡带](https://tiansongyu.github.io/open-console-cad/?device=gameboy&view=accessories#viewer) · [分层爆炸](https://tiansongyu.github.io/open-console-cad/?device=gameboy&view=exploded#viewer)

<a href="https://tiansongyu.github.io/open-console-cad/?device=gameboy&amp;view=assembled#viewer"><img src="../../site/public/images/gameboy/hero.webp" width="360" alt="初代灰色 Game Boy DMG-01 的 FreeCAD 模型"></a>

本模型采用 1989 年初代灰色 DMG-01 外观，经过 **15 轮建模与修正，包含 410 个组件条目、768 个实体**。保留单色屏幕、十字键、酒红色 A/B 键、倾斜 START/SELECT 键、六孔扬声器格栅、音量与对比度滚轮、背部卡带槽和可拆电池盖。

内部包含四节 AA 电池、弹簧与片状触点、前后电路板、电源与耳机小板、CPU/RAM 封装、按键胶垫、LCD 固定框、扬声器及焊接互连。独立空白 Game Pak 卡带包含分壳、PCB、32 接点和 ROM 封装示意。

## 下载与查看

- [完整 FreeCAD 模型](output/GameBoy_Complete.FCStd) · [爆炸装配](output/GameBoy_Exploded.FCStd)
- [FreeCAD 原生图纸](output/GameBoy_Drawings.FCStd) · [12 页 A3 PDF 图册](output/drawings/GameBoy_Drawings.pdf) · [SVG 图页](output/drawings/)
- [整套 STEP](output/GameBoy_FullKit.step) · [主机 STEP](output/GameBoy_Handheld.step) · [爆炸 STEP](output/GameBoy_Exploded.step)
- [零件清单](output/COMPONENTS.csv) · [逐轮记录](ITERATIONS.md) · [检查报告](output/reports/)

整套文件包含 367 个主机组件和 43 个卡带组件。网页提供整机、背面、内部结构、显示层、按键机构、主板、电池和卡带等视图；拖动“展开程度”可查看各装配层。卡带采用通用学习标识，不包含游戏 ROM 或游戏封面。

## 在 FreeCAD 中修改和重建

使用 FreeCAD 1.1.3 运行 `Open_GameBoy.FCMacro`，同时打开完整模型、爆炸装配和原生图纸，也可单独打开需要的文件。工程保留外壳草图、尺寸约束、凸台、大小角圆角和布尔加工历史；每个物理组件保存编号、分组与材质角色。

`Parameters` 保存宽、高、完整厚度与机壳基准；部分草图通过表达式引用宽高。接口、孔位、内部零件仍使用显式坐标，修改主参数后应重新检查装配。30.8 mm 是本模型的机壳基准，**32 mm 是包含控制件的完整整机厚度**。

运行 `Rebuild_GameBoy.FCMacro` 会依次执行全部 15 轮源码，输出至 `output/rebuilt/`，保留正式交付文件。入口位于 `scripts/iterNN_*.py`，主要实现为 `../../tools/cadlib/gameboy.py`；重建时请保留仓库结构。

`scripts/drawing_geometry.py` 从实际 BRep 生成投影与平面剖面，再运行 `python3 tools/cadlib/build_book.py devices/gameboy`，通过 Kami 管线生成图册。原生图纸包含自包含 SVG 图页与可测量的原生尺寸参考；修改模型后需要重新生成图纸。

网页网格使用 0.10 mm 线性偏差、0.15 rad 角度偏差，保留组件标识、颜色和爆炸偏移。GLB 用于交互预览，继续设计请使用 FCStd 或 STEP。

## 尺寸与版本依据

| 项目 | 参数 | 依据 |
| --- | --- | --- |
| 完整整机包络 | 90 × 148 × 32 mm | 任天堂公开宽、高、厚度 |
| LCD 显示区 | 47 × 43 mm | 任天堂公开规格 |
| 原机分辨率 | 160 × 144 像素 | 公开规格；CAD 不模拟图像显示 |
| 供电形式 | 四节 AA 电池 | 原始 DMG-01 结构 |
| 独立卡带外形 | 约 57 × 65 mm | 本模型学习尺寸 |
| 版本 | 初代灰色 DMG-01 | 单色非背光屏幕，圆形 A/B 按键 |

来源见 [SOURCES.md](references/SOURCES.md)。内部布局参考拆机中的具体主板修订版，不代表所有生产批次；没有采用 Game Boy Pocket、Color、IPS 背光改装或充电电池改装。局部轮廓、壁厚、封装、孔位、接点、线缆和配合间隙为近似学习几何，不定义电路或制造公差。

## 验证记录

全部 15 轮源码重新运行后，410 个组件通过核对。627 对候选组件进行实体求交，未发现超过检查阈值的实体穿插。原生完整模型、爆炸装配及三份 STEP 回读通过；交换格式按实体匹配，必要时以双向布尔差集核对几何。

26 项直接模型尺寸和 14 项原生图纸尺寸参考通过检查。12 页 A3 图册涵盖外观、接口、显示、按键、真实剖面、爆炸装配、电路板、电池、卡带、组件索引和来源说明；字体、内容、排版与逐页视觉结果见 `output/reports/`。

原创内容采用根目录 MIT 协议；第三方名称、设计、字体与参考材料见 [第三方声明](../../THIRD_PARTY_NOTICES.md)。
