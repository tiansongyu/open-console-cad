# Nintendo Switch · FreeCAD 项目

[在线整机预览](https://tiansongyu.github.io/open-console-cad/?device=switch&view=assembled#viewer) · [在线爆炸视图](https://tiansongyu.github.io/open-console-cad/?device=switch&view=exploded#viewer) · [仓库使用说明](../../README.md)

16 轮设计，654 个组件、835 个实体。包含主机、左右手柄、底座、非充电握把与两套腕带。整体包络参考官方数据，局部尺寸和内部结构为近似示意。

2026-10-13 外形精修针对初代 HAC-001：重新建立 Joy-Con 外轮廓及前后壳的厚度方向圆角，缩窄肩键并重塑扳机，校正摇杆、按键、扬声器和亮度传感器位置。对比同一视角的[原边缘](output/previews/edge_before.png)与[新边缘](output/previews/edge_after.png)，或查看[独立虚拟桌面截图](output/previews/virtual_desktop_final.png)。圆角和局部坐标依据官方照片拟合，未使用原厂 CAD 或实物扫描，不能视为制造级复刻。

[![模型总览](output/previews/overview.png)](https://tiansongyu.github.io/open-console-cad/?device=switch&view=assembled#viewer)

## 打开文件

- [完整模型](output/Switch_Complete.FCStd)：保留草图、凸台、圆角、布尔操作与参数表。
- [爆炸装配](output/Switch_Exploded.FCStd)：独立组件与爆炸位移。
- [FreeCAD 图纸](output/Switch_Drawings.FCStd)：12 页自包含图页与原生尺寸参考。
- [A3 PDF 图册](output/drawings/Switch_Drawings.pdf)：总装、接口、剖面、爆炸和材料索引。
- [带色整套 STEP](output/Switch_FullKit.step) · [手持整机 STEP](output/Switch_Handheld.step) · [底座 STEP](output/Switch_Dock.step)。
- [组件清单](output/COMPONENTS.csv) · [效果图](output/previews/) · [检查报告](output/reports/)。

在 FreeCAD 中运行 `Open_Switch.FCMacro` 可打开主要成品；运行 `Rebuild_Switch.FCMacro` 会将各轮结果生成到 `output/rebuilt/`，保留当前交付。已验证 FreeCAD 1.1.3。

## 源码与维护

- [逐轮源码索引](ITERATIONS.md)。历史二进制检查点不提交，可运行重建宏生成。
- 新增 12 个原生圆角特征，分别关联 `JoyOuterRadius`、`JoyInnerRadius`、`JoyFrontRoll`、`JoyRearRoll`。参数表中的主机后缘圆角和按钮间距仅记录设计值，修改它们需要重新执行相应建模代码。参数修改后需重新检查上下游几何与配合。
- 图纸为当前模型快照，修改模型后需要重新生成。
- 网页网格由实际 FCStd 导出，详细维护方法见 [维护指南](../../docs/MAINTAINING.md)。
- 公开尺寸、局部近似和参考链接见 [SOURCES.md](references/SOURCES.md)。

## 许可

原创内容按仓库 [MIT](../../LICENSE) 授权；第三方名称、标识、字体与参考资料见 [第三方声明](../../THIRD_PARTY_NOTICES.md)。

本版检查见[外形与原生特征](output/reports/exterior_refinement_audit.json)、[装配干涉](output/reports/16_interference_audit.json)、[导出回读](output/reports/export_roundtrip_audit.json)及[图纸尺寸](output/reports/drawing_checks.json)。尺寸由已保存的原生 BRep 使用 `optimalBoundingBox(False, False)` 重新测量；手持整机为 239 × 102 mm，主机厚 13.9 mm，含摇杆和扳机的最大厚度为 28.4 mm。

本轮从第 14 轮成品执行第 15–16 轮并重新导出。回读检查使用 `audit_exports.py output --saved-geometry --surface-fallback=JoyRRear` 比较已保存 BRep，不代表全历史重算或参数编辑测试。右后壳的重合曲面布尔差运算耗时异常，因此该零件使用双向表面采样距离确认，采样不等同于解析几何恒等证明。旧的 `14_interference_audit.json`、`rebuild_verification.json`、`parameter_edit_test.json`、`measurement_refresh.json` 等报告及 `Switch_Cutaway.FCStd` 保留为历史资料，不代表本版验证。
