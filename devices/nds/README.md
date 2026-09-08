# Nintendo DS · NTR-001 初代

正在制作中的 FreeCAD CAD 学习模型。当前已完成外壳、等大的双 3 英寸显示组件、中央铰链、按键、DS / GBA 双卡槽、电池、主板与射频模块、排线和紧固件，共 10 轮、314 个组件。

本目录尚未作为完成模型加入网页；下一步是修正开合配合、独立源码重建、精确导出和图纸验证。局部外形和内部布局为近似研究模型。

- 公开闭合尺寸：148.7 × 84.7 × 28.9 mm。
- 版本：NTR-001；不是 DS Lite / DSi。
- 依据：[来源清单](references/SOURCES.md)。
- 迭代入口：`scripts/iterNN_*.py`，共用原生建模代码位于 `../../tools/cadlib/nds.py`。
- 检查记录：`output/reports/`；阶段效果图：`output/previews/`。
- 建模通过 [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp) 的主线程执行接口完成。
