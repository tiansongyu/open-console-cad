# Nintendo DS NTR-001

[在线展开预览](https://tiansongyu.github.io/open-console-cad/?device=nds&view=assembled#viewer) · [闭合预览](https://tiansongyu.github.io/open-console-cad/?device=nds&view=closed#viewer) · [分层爆炸](https://tiansongyu.github.io/open-console-cad/?device=nds&view=exploded#viewer)

[![Nintendo DS](../../site/public/images/nds/hero.webp)](https://tiansongyu.github.io/open-console-cad/?device=nds&view=assembled#viewer)

初代 NTR-001 银色厚机身，完成 15 轮设计、321 个物理组件和 424 个实体。包括两块同尺寸显示屏、中央铰链、十字键、ABXY、系统键、L/R、双扬声器、DS Slot-1 与 GBA Slot-2、电池仓、主板、射频子板、排线和固定长度触控笔。版本为最早的 Nintendo DS。

## 成品文件

- [完整展开模型](output/NintendoDS_Complete.FCStd)
- [闭合模型](output/NintendoDS_Closed.FCStd)
- [分层爆炸模型](output/NintendoDS_Exploded.FCStd)
- [FreeCAD 图纸](output/NintendoDS_Drawings.FCStd)
- [12 页 A3 PDF 图册](output/drawings/NintendoDS_Drawings.pdf)
- [整套 STEP](output/NintendoDS_FullKit.step) · [主机 STEP](output/NintendoDS_Handheld.step) · [闭合 STEP](output/NintendoDS_Closed.step) · [爆炸 STEP](output/NintendoDS_Exploded.step)
- [零件清单](output/COMPONENTS.csv) · [检查报告](output/reports/) · [迭代源码](scripts/)

## 使用与重建

在 FreeCAD 1.1.3 中执行 `Open_NintendoDS.FCMacro` 打开主要文件。修改参数表 `Parameters.Opening` 后，执行 `Apply_Pose_NintendoDS.FCMacro` 应用开合角度，范围为 0–150°；0° 为闭合。铰链坐标保存在模型参数表和 StudyInfo 中，不依赖原来的会话。

`Rebuild_NintendoDS.FCMacro` 顺序重建 15 阶段，并将新文件写入 `output/rebuilt/`，保留交付文件。分轮入口在 `scripts/iterNN_*.py`，共享几何实现位于仓库 `tools/cadlib/`。必须保留完整仓库结构。

图纸是当前几何的快照，改模后需重新生成。网页 GLB 保留组件身份、颜色、爆炸位移和铰链参数；网页网格不能替代精确 CAD 实体。

## 尺寸与验证

闭合包络为 **148.7 × 84.7 × 28.9 mm**。两块屏幕均为 3 英寸、4:3；本模型将其换算为 60.96 × 45.72 mm 显示窗口。局部外形、孔位、壁厚、PCB 和封装等为近似研究模型，依据见 [SOURCES.md](references/SOURCES.md)。

- 321 个组件独立源码重建匹配，原生文件与四份 STEP 回读通过。
- 展开 599 对、闭合 491 对候选组件均完成逐组件实体求交，未发现超过 0.000001 mm³ 的穿插，候选数量见最终报告。
- 18 项直接模型尺寸及 18 项原生图纸尺寸参考核对通过。
- 0°、75°、150° 的原生开合宏检查通过。
- 12 页图册通过 Kami 字体、内容、版式、密度与逐页视觉检查。

图册包含展开总装、闭合三视图、双屏尺寸、按键与双卡槽详图、真实 BRep 剖面、整机及上下机身爆炸图、主板与电池、触控笔与电池仓、材料索引和尺寸来源。

[逐轮迭代与效果图](ITERATIONS.md)。历史问题已在后续轮次修正；使用最终原生文件和 `final_*` 检查报告。原创代码遵循仓库 MIT，第三方权利说明见根目录。
