# Sony PSP-1000 初代

[整机 3D 预览](https://tiansongyu.github.io/open-console-cad/?device=psp&view=assembled#viewer) · [内部结构](https://tiansongyu.github.io/open-console-cad/?device=psp&view=internal#viewer) · [UMD 光驱](https://tiansongyu.github.io/open-console-cad/?device=psp&view=drive#viewer) · [分层爆炸](https://tiansongyu.github.io/open-console-cad/?device=psp&view=exploded#viewer)

[![PSP-1000 原生模型](../../site/public/images/psp/hero.webp)](https://tiansongyu.github.io/open-console-cad/?device=psp&view=assembled#viewer)

本项目研究初代 PSP-1000：黑色圆端机身、银色周缘、单模拟滑杆、四向键、几何符号面按键、HOME 系统键列、Mini-USB、红外、记忆棒和 UMD 光驱。模型经过 14 轮迭代，包含 346 个组件、437 个实体。内部为主要模块和装配关系的近似示意，未包含真实电路、固件或游戏内容。

## 下载文件

- [完整模型](output/PSP1000_Complete.FCStd) · [爆炸装配](output/PSP1000_Exploded.FCStd)
- [FreeCAD 原生图纸](output/PSP1000_Drawings.FCStd) · [12 页 A3 PDF 图册](output/drawings/PSP1000_Drawings.pdf)
- [整套 STEP](output/PSP1000_FullKit.step) · [主机 STEP](output/PSP1000_Handheld.step) · [爆炸 STEP](output/PSP1000_Exploded.step)
- [零件清单](output/COMPONENTS.csv) · [逐轮迭代](ITERATIONS.md) · [检查报告](output/reports/)

完整文件包含主机、空白 UMD 卡壳、光盘和记忆棒。主机 STEP 单独导出主机；网页可以分别查看电子模块、操作机构、接口及可拆介质。

## 在 FreeCAD 中打开与重建

使用 FreeCAD 1.1.3，运行本目录的 `Open_PSP1000.FCMacro`，打开完整模型、爆炸装配和图纸。也可以直接打开 `output/*_Complete.FCStd`。模型树保留外壳的原生草图、尺寸约束、凸台、圆角和布尔建模历史；组件带有 `PartID`、`PartNumber`、装配分组与材质说明。

参数表 `Parameters` 保存主体尺寸等输入。部分外壳宽高通过表达式连接到参数表；局部孔位、封装和排线采用显式坐标，修改主尺寸后应重新检查这些配合。

`Rebuild_PSP1000.FCMacro` 执行全部 14 阶段，将新模型、STEP 和预览写入 `output/rebuilt/`，保留交付文件。逐轮入口为 `scripts/iterNN_*.py`，共享实现位于仓库 `tools/cadlib/psp.py`。运行时需保留完整仓库目录结构。

图纸是当前几何的快照，改模后需重新生成。`scripts/drawing_geometry.py` 在 FreeCAD Python 环境中投影实际 BRep；`tools/cadlib/build_book.py devices/psp` 使用 Kami 构建 PDF，并需要继续执行内容、字体和逐页视觉检查。原生图页由 `cadlib.native_sheets.create_native_sheets(model)` 生成，保留自包含 SVG 和可测尺寸参考。

## 尺寸依据

| 项目 | 尺寸 | 依据 |
| --- | --- | --- |
| 主体包络 | 170 × 74 × 23 mm | 索尼公开规格，明确不含最大突出部位 |
| 本模型含按键包络 | 170 × 74 × 23.9 mm | 当前模型测量，局部尺寸近似 |
| 显示窗口 | 95.19 × 53.55 mm | 4.3 英寸、16:9 的几何换算 |
| UMD 卡壳 | 65 × 64 × 4.2 mm | 索尼公布的外形参考 |
| UMD 光盘 | 直径 60 mm | 索尼公布的光盘直径 |
| PSP-110 电池 | 1800 mAh 标识 | 原始说明书；外壳和电芯几何为示意 |

具体链接见 [SOURCES.md](references/SOURCES.md)。初代型号以官方说明书的控制件、接口和容量为依据，社区拆解照片用于相对布局参考。局部曲面、壁厚、孔位、光学和机械细节不代表厂商制造数据。

## 验证范围

- 346 个物理组件逐件进行独立源码重建比对。
- 原生整机、爆炸模型和三份 STEP 回读；检查有效性、实体对应关系、包络及必要的双向布尔差集。
- 最终 474 对候选组件逐对实体求交，阈值为 0.000001 mm³。
- 23 项直接模型尺寸、19 项原生图纸尺寸参考核对。
- 12 页 A3 图册包含外观、接口、真实剖面、主板与电池、UMD、操作机构、介质和材料索引；通过 Kami 字体、内容和逐页检查。
- 网页 GLB 从同一组 BRep 导出，保留组件编号、颜色、分组和爆炸位移；当前 PSP 预览使用 0.10 mm 线性偏差和 0.15 rad 角度偏差以保留圆弧外观；网格用于展示，继续设计应使用 FCStd 或 STEP。

原创内容遵循根目录 MIT 协议；第三方名称、标识、字体和参考材料的权利说明见 [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md)。
