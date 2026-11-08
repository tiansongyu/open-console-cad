# Nintendo Super Famicom · SHVC-001

早期日版 SHVC-CPU-01 / 独立 SHVC-SOUND 结构学习模型包含 **22 轮源码、1,925 个组件条目与 2,264 个实体**：原生曲面分体外壳、主板、分立 CPU / PPU、上下 62P 卡槽连接器、独立声卡、RF 模块、屏蔽、退卡机构及前板排线；另含两只原版 SHVC-005 手柄和另售 HVC-002 / SHVC-008 学习附件。提供完整及爆炸原生工程、三份 STEP、12 页 A3 PDF / SVG / 原生图纸和 25 个网页视图。

<table>
<tr>
<td align="center" width="33%"><a href="output/previews/final_hero.png"><img src="output/previews/final_hero.png" width="206" height="160" alt="日版原机与双手柄"></a><br>日版原机与双手柄</td>
<td align="center" width="33%"><a href="output/previews/final_front.png"><img src="output/previews/final_front.png" width="206" height="160" alt="曲面外壳与原版接口"></a><br>曲面外壳与原版接口</td>
<td align="center" width="33%"><a href="output/previews/final_internal.png"><img src="output/previews/final_internal.png" width="206" height="160" alt="主板、独立声卡与卡槽"></a><br>主板、独立声卡与卡槽</td>
</tr>
<tr>
<td align="center" width="33%"><a href="output/previews/final_exploded.png"><img src="output/previews/final_exploded.png" width="206" height="160" alt="分层爆炸装配"></a><br>分层爆炸装配</td>
<td align="center" width="33%"><a href="output/previews/final_controller.png"><img src="output/previews/final_controller.png" width="206" height="160" alt="原版狗骨形手柄"></a><br>原版狗骨形手柄</td>
<td align="center" width="33%"><a href="output/previews/final_accessories.png"><img src="output/previews/final_accessories.png" width="206" height="160" alt="另售 AC 适配器与 AV 线"></a><br>另售 AC 适配器与 AV 线</td>
</tr>
</table>

- [在线 3D 预览](https://tiansongyu.github.io/open-console-cad/?device=sfc&view=assembled#viewer)
- [完整 FreeCAD 工程](output/SuperFamicom_Complete.FCStd) · [爆炸工程](output/SuperFamicom_Exploded.FCStd) · [打开宏](Open_SuperFamicom.FCMacro)
- [全套 STEP](output/SuperFamicom_FullKit.step) · [主机与双手柄 STEP](output/SuperFamicom_Console.step) · [爆炸 STEP](output/SuperFamicom_Exploded.step)
- [12 页 A3 PDF](output/drawings/SuperFamicom_Drawings.pdf) · [HTML 图册](output/drawings/SuperFamicom_Drawings.html) · [SVG 目录](output/drawings/) · [原生图纸](output/SuperFamicom_Drawings.FCStd)
- [组件清单](output/COMPONENTS.csv) · [模型清单](output/reports/final_manifest.json)
- [完整重建宏](Rebuild_SuperFamicom.FCMacro) · [逐轮记录](ITERATIONS.md) · [建模源码](../../tools/cadlib/sfc.py)
- [本轮源码重放比对](output/reports/fidelity_source_replay.json) · [严格实体检查](output/reports/fidelity_strict.json) · [装配求交](output/reports/fidelity_interference.json)
- [STEP 回读](output/reports/export_roundtrip_audit.json) · [参数编辑复原](output/reports/parameter_edit_test.json) · [资料与边界](references/SOURCES.md)

使用 FreeCAD 1.1.3 打开工程。下壳草图与拉伸、上壳分段放样、狗骨形手柄轮廓和布尔历史保留修改入口；重建宏从空文档执行全部轮次，并写入 `output/rebuilt/`。`Parameters.Width` 驱动底壳原生宽度约束；其他局部几何并非一键缩放的制造设计。

日版 SHVC-001 原使用说明书的名义包络为 **200 × 242 × 74 mm**。选择带独立声卡的早期 SHVC-CPU-01，不混用后期 1CHIP 主板或复刻迷你机。任天堂 1992 年维修手册指导上下 62P 连接器、扁平排线、磁芯、退卡机构和装配分件。

两只 SHVC-005 手柄采用实物照片所示 1992 年双移位寄存器板，保留四色凸面键、斜置 Start / Select、独立肩键和七接点插头。主机原装配置含两只手柄；HVC-002 线性 AC 适配器与 SHVC-008 AV 线另售。附件内部和缩短的展示线缆按原版实物照片表达，不混入现代替换电源。

壁厚、曲率、孔位、弹簧、导电胶、元件、走线和附件尺寸均为非功能性学习近似；不提供制造公差、工作电路或接口配合保证。原版外包络、实物结构依据与局部近似在图册和资料页中分别说明。

第 22 轮校正了卡座 2.50 mm 节距和两处分区间隔、左右手柄口与配套插头、前板外侧圈号、POWER 凸起、浅色控制边框、指示灯与图文比例，并按兼容接口资料修订 DC/RCA 尺寸。原有 1,918 个组件标识和编号保留，新增 7 个外观组件。

当前 1,925 个组件通过严格 BRep 检查，2,647 对装配求交无超过 0.000001 mm³ 的干涉。第 22 轮从独立载入的第 21 轮历史重放，逐件与交付模型核对；本轮未从空文档重跑全部 22 轮，也未重复历史参数编辑测试。36 项校准特征、3 份 STEP 回读、12 页图纸与 25 种网页视图按当前文件核对，详见 [交付报告](output/reports/fidelity_delivery_checks.json)。

旧版本 `efc601d` 的线上检查保留为历史记录；它不覆盖第 22 轮的新文件。当前来源、照片拟合方法与未确认尺寸见 [第 22 轮证据](references/fidelity_iteration22.json)。
