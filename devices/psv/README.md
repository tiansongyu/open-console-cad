# PlayStation Vita · PCH-1000 Wi-Fi OLED

[整机 3D 预览](https://tiansongyu.github.io/open-console-cad/?device=psv&view=assembled#viewer) · [内部结构](https://tiansongyu.github.io/open-console-cad/?device=psv&view=internal#viewer) · [后触控结构](https://tiansongyu.github.io/open-console-cad/?device=psv&view=rear-touch#viewer) · [分层爆炸](https://tiansongyu.github.io/open-console-cad/?device=psv&view=exploded#viewer)

[![初代 PS Vita CAD 模型](../../site/public/images/psv/hero.webp)](https://tiansongyu.github.io/open-console-cad/?device=psv&view=assembled#viewer)

本项目按初代 PCH-1000 Wi-Fi OLED 建模，保留 5 英寸 OLED、双模拟摇杆、前后摄像头、前后电容触控、银色周缘、椭圆握持垫和闭合腕带环。原生模型经过 14 轮迭代，包含 386 个组件、845 个实体，涵盖独立左右操作板、电池固定结构、主要电子模块、专用接口及空白可拆介质。

## 下载文件

- [完整模型](output/PSVita_Complete.FCStd) · [爆炸装配](output/PSVita_Exploded.FCStd)
- [FreeCAD 图纸](output/PSVita_Drawings.FCStd) · [12 页 A3 PDF 图册](output/drawings/PSVita_Drawings.pdf)
- [整套 STEP](output/PSVita_FullKit.step) · [主机 STEP](output/PSVita_Handheld.step) · [爆炸 STEP](output/PSVita_Exploded.step)
- [零件清单](output/COMPONENTS.csv) · [逐轮迭代](ITERATIONS.md) · [检查报告](output/reports/)

整套文件包含主机和空白游戏卡、存储卡示意。主机 STEP 单独保留主机组件；网页可以分组查看双摇杆机构、后触控、电池、光学音频和电子模块。

## 使用与重建

使用 FreeCAD 1.1.3 运行 `Open_PSVita.FCMacro`，或直接打开 `output/*_Complete.FCStd`。模型保留外壳的原生草图、约束、凸台、圆角和布尔历史，组件具有 `PartID`、`PartNumber`、分组和材质说明。

`Parameters` 保存主体尺寸，部分宽高表达式连接到原生外壳草图。局部孔位、封装和排线为显式坐标，改变主参数后需要复查配合。

`Rebuild_PSVita.FCMacro` 按序执行 14 轮源码，将模型、STEP 和预览写到 `output/rebuilt/`，保留交付文件。逐轮入口在 `scripts/`，主要实现为仓库 `tools/cadlib/psv.py`；应保留整个仓库结构。

图纸是当前模型的版本快照，改模后应重新执行 `scripts/drawing_geometry.py`、Kami PDF 构建及逐页检查。PDF 构建命令为 `python3 tools/cadlib/build_book.py devices/psv`。原生图页使用自包含 SVG 与可测尺寸参考，不会自动跟随所有三维修改。

网页网格通过实际 BRep 导出，使用 0.10 mm 线性偏差和 0.15 rad 角度偏差保留圆弧外观。下载 FCStd 或 STEP 继续设计；GLB 用于浏览器展示。

## 尺寸与版本依据

| 项目 | 尺寸 / 参数 | 依据 |
| --- | --- | --- |
| 主体包络 | 182 × 83.5 × 18.6 mm | 索尼规格，不含最大突出部位 |
| 含摇杆厚度 | 24.05 mm | 当前模型测量；局部尺寸近似 |
| 显示窗口 | 110.69 × 62.26 mm | 5 英寸 16:9 的几何换算 |
| 电池标识 | 2210 mAh / 3.7 V | 索尼规格；电芯和壳体几何为示意 |
| 版本 | PCH-1000 Wi-Fi OLED | 用户确认的初代型号 |

参考依据见 [SOURCES.md](references/SOURCES.md)。iFixit 的拆解对象为 3G 型号，本模型只取其共有结构作为照片参考，不加入蜂窝通信、SIM 或 GPS 模块。

局部外形、壁厚、孔位、封装、印纹、接点和内部间隙为近似学习模型，不包含真实电路、固件、引脚定义或制造公差。后触控印纹由简化几何符号组成；重复印纹按一个组件记录，实体数单独统计。

## 检查范围

原生装配通过 781 对候选组件的实体求交、386 个组件独立源码重建及三份 STEP 回读。25 项直接尺寸、17 项原生图纸尺寸参考核对通过。图册包含正反面、接口、真实剖面、OLED、双触控、双摇杆、主板、电池、光学音频和介质视图，并执行 Kami 字体、内容与逐页视觉检查。具体数量和阈值以 `output/reports/` 的最终记录为准。

原创内容遵循根目录 MIT 协议。第三方名称、标识、字体和参考材料的权利说明见 [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md)。
