# 全模型实机校准计划

本轮从 Nintendo DS NTR-001 开始，覆盖模型库全部 27 款设备及其已建模控制器、附件。目标是依据实机资料逐款改进尺寸、轮廓、接口、按键和结构，并同步 CAD、STEP、图纸与网页预览。当前状态为进行中，尚无设备完成本轮验收。

进度与基线保存在 [fidelity_progress.json](fidelity_progress.json)。开始日期为 2026-11-08。

## 证据与完成条件

总体尺寸优先使用同型号、同地区版本的原厂规格、手册和维修资料。局部轮廓和布局可参考实机照片、拆解与可追溯测量；图片拟合记录视角、比例基准和误差来源。无法查证的尺寸保留为估算，不用零件数量或几何检查通过代替实机一致性证明。

完全 1:1 的制造级复刻需要原厂公差资料或实机测量，现有资料尚不能证明所有表面、孔位、壁厚与内部零件都与实机完全一致。该限制不阻止继续修正有依据的差异。

每款按以下顺序完成：

1. 固定型号、地区、主板或手柄版本，核对资料适用范围。
2. 对照已有原生模型与实机资料，记录可确认差异及待查尺寸。
3. 修订可重建源码和模型，保持组件标识及合理的装配关系。
4. 检查当前保存的 BRep、整机包络、装配干涉；翻盖设备覆盖闭合、展开和中间姿态。
5. 验证源码重建、STEP 回读和参数修改；更新受影响图纸、预览及文件哈希。
6. 完成当前版本的视觉对照和仓库检查，记录剩余差异后提交并推送该轮改动，保留提交号，再标记该轮完成。按用户要求，每轮验证通过后单独提交和推送。

CAD 几何修改与渲染使用独立虚拟桌面和独立 FreeCAD 配置，遵循 [MCP 运行说明](MCP.md)。不操作用户当前桌面。输出同步遵循 [维护流程](MAINTAINING.md)。

## 设备顺序

顺序以 NDS 为起点，随后按掌机及主机家族安排。资料研究可并行，完成状态按每款的当前文件证据更新。下表组件数和历史轮次来自开始时的交付清单。

| 顺序 | 设备与版本 | 历史轮次 | 基线组件数 | 本轮状态 |
| ---: | --- | ---: | ---: | --- |
| 1 | [Nintendo DS · NTR-001](../devices/nds/README.md) | 16 | 321 | 第 17 轮已验证 |
| 2 | [Nintendo 3DS · CTR-001](../devices/3ds/README.md) | 14 | 324 | 第 15 轮已验证 |
| 3 | [Sony PSP-1000 · PSP-1000](../devices/psp/README.md) | 15 | 346 | 候选模型验证中 |
| 4 | [PlayStation Vita · PCH-1000 Wi-Fi OLED](../devices/psv/README.md) | 15 | 386 | 待开始 |
| 5 | [Steam Deck · 2022 LCD](../devices/steamdeck/README.md) | 16 | 498 | 待开始 |
| 6 | [Nintendo Switch · HAC-001](../devices/switch/README.md) | 18 | 654 | 待开始 |
| 7 | [Nintendo Switch 2 · BEE-001](../devices/switch2/README.md) | 16 | 799 | 候选模型验证中 |
| 8 | [Nintendo Game Boy · DMG-01 (1989)](../devices/gameboy/README.md) | 15 | 410 | 待开始 |
| 9 | [Nintendo Game Boy Advance · AGB-001 Indigo · early AGB-CPU-02](../devices/gba/README.md) | 17 | 779 | 待开始 |
| 10 | [Nintendo Game & Watch · DK-52 · Donkey Kong · Original 1982](../devices/gamewatch/README.md) | 15 | 592 | 待开始 |
| 11 | [Nintendo Famicom · HVC-001 · 圆形按键](../devices/famicom/README.md) | 16 | 634 | 待开始 |
| 12 | [Nintendo Super Famicom · SHVC-001 · SHVC-CPU-01 · Original Japan](../devices/sfc/README.md) | 21 | 1,918 | 待开始 |
| 13 | [Nintendo 64 · NUS-001 · 初代灰色](../devices/n64/README.md) | 15 | 747 | 待开始 |
| 14 | [Nintendo Wii · RVL-001 · 初代白色](../devices/wii/README.md) | 15 | 654 | 待开始 |
| 15 | [Nintendo Wii U · WUP-001 · 首发白色 Basic](../devices/wiiu/README.md) | 22 | 707 | 待开始 |
| 16 | [Atari 2600 · CX2600 · Heavy Sixer (1977)](../devices/atari2600/README.md) | 23 | 684 | 待开始 |
| 17 | [Sega Mega Drive · HAA-2510 · 初代日版](../devices/megadrive/README.md) | 13 | 825 | 候选模型验证中 |
| 18 | [Sega Saturn · HST-3200 · 初代日版灰色](../devices/saturn/README.md) | 22 | 715 | 待开始 |
| 19 | [Sony PlayStation · SCPH-1000 · 初代日版灰色](../devices/ps1/README.md) | 25 | 929 | 待开始 |
| 20 | [Sony PlayStation 2 · SCPH-10000 · 初代日版黑色](../devices/ps2/README.md) | 34 | 1,352 | 待开始 |
| 21 | [Sony PlayStation 3 · CECHA00 · 日本原版 60 GB](../devices/ps3/README.md) | 30 | 1,592 | 待开始 |
| 22 | [Sony PlayStation 4 · CUH-1000A · 初代黑色](../devices/ps4/README.md) | 29 | 1,039 | 待开始 |
| 23 | [Sony PlayStation 5 · CFI-1000A 系列 · 原版光驱](../devices/ps5/README.md) | 34 | 1,635 | 待开始 |
| 24 | [Microsoft Xbox · Original Black v1.0 · 2001 · Duke](../devices/xbox/README.md) | 18 | 978 | 待开始 |
| 25 | [Microsoft Xbox 360 · Premium 20 GB · Xenon · 北美原版](../devices/xbox360/README.md) | 35 | 2,005 | 待开始 |
| 26 | [Microsoft Xbox One · Model 1540 · 500 GB · Original 2013](../devices/xboxone/README.md) | 28 | 1,791 | 待开始 |
| 27 | [Microsoft Xbox Series X · Original optical · 2020 · 1 TB](../devices/seriesx/README.md) | 19 | 1,047 | 待开始 |

## 基线发现

初始清单共 24,361 个组件；各设备清单都明确包含近似局部几何或示意内部结构。25 款使用 `profile.json` 与共享 `cadlib`，Switch 和 Switch 2 使用独立分轮脚本。现有验证报告只证明其记录版本的几何及交付一致性，本轮需针对修改后的文件重验。

2026-11-08 已完成 [27 款原生模型基线检查](fidelity_baseline_audit.json)：24,361 个组件的保存后实体、组件身份和清单边界核对通过，所有输入文件在检查期间哈希不变。本次未重计算历史、未执行装配求交，也未验证实机一致性。Series X 的 HDMI、以太网和三处 USB-A 均只建了 4 个接点；按已识别接口类型，应分别核对为 19、8、9 个配合接点。规则依据来自 [TE HDMI 规格](https://www.te.com/en/product-2007435-1.html)、[TE RJ45 规格](https://www.te.com/en/product-5406443-1.html)、[TE USB 3.0 Type-A 规格](https://www.te.com/en/product-1932258-1.html)及 [Xbox Series X 接口规格](https://www.xbox.com/en-US/consoles/xbox-series-x)。这些通用接口资料不证明主机使用了对应 TE 料号。

以下是交付清单记录的包络差值，尚未在本轮重测。测量范围可能包含接口、脚垫、标识或可拆硬盘，不能直接据此缩放整机；须先核对实机规格对“外形尺寸”的定义。

| 设备 | 清单测量值减参考值，X / Y / Z（mm） | 后续核对 |
| --- | --- | --- |
| Nintendo Game & Watch | +0.000 / +0.000 / +0.136 | 合盖局部突出与测量样本口径 |
| Nintendo 64 | +0.000 / +0.000 / +0.070 | 顶面标识或局部突出 |
| Nintendo Wii | +0.000 / +0.358 / +0.000 | 前后局部突出 |
| Nintendo Wii U | +0.000 / +0.278 / +1.200 | 脚垫和控制件，区分塑料机身包络 |
| Sega Mega Drive | +0.000 / +0.500 / +0.028 | 接口与标识突出 |
| Sega Saturn | +0.000 / +0.298 / +0.350 | 后部接口、标识和版本适用性 |
| Sony PlayStation | +0.000 / +0.900 / +0.043 | 后部接口与标识；参考值为近似尺寸 |
| Sony PlayStation 2 | +0.000 / +3.450 / +0.043 | 后部突出与机身尺寸排除项 |
| Sony PlayStation 3 | +0.000 / +0.000 / +1.318 | 脚垫、外壳及尺寸排除项 |
| Sony PlayStation 4 | +0.000 / -0.509 / +0.000 | 斜面壳体的最远端定义 |
| Sony PlayStation 5 | +0.000 / +0.000 / -0.066 | 壳体曲面与“约”尺寸 |
| Microsoft Xbox | +0.000 / +0.276 / -0.400 | 局部突出与官方近似尺寸 |
| Microsoft Xbox 360 | +21.850 / +1.538 / +0.627 | 可拆硬盘是否纳入包络，避免把含硬盘范围与裸机规格比较 |

NDS 的 `profile.json` 保留 `lower_display_y=-1`、`upper_display_y=77`，共享源码在第 2 轮改为 `4` 和 `84`；基线检查确认保存的 `StudyInfo.ProfileJSON` 也是 `4` 和 `84`。校准时应共同核对最终原生几何、保存参数和完整源码执行结果，避免只读初始参数误判当前位置。

## 验证入口

- `tools/cadlib/audit_assembly.py`：重新打开原生文件，检查实体、候选组件干涉和姿态；分批运行必须最终 `complete=true` 且 `passed=true`。
- `tools/cadlib/audit_exports.py`：检查原生文件、逐实体 STEP 回读与颜色。
- `tools/cadlib/compare_native.py`：比较源码重建与交付模型。
- `tools/export_web_models.py`、`tools/compress_web_models.py`：导出当前模型与压缩预览，随后同步目录元数据。
- `tools/audit_collection.py`：汇总当前保存的原生几何与交付文件；不替代实机对照。
- `tools/audit_fidelity.py`：只读核对当前完整模型的实体、包络、组件身份和已指定接口触点数，输出绑定文件哈希的基线；不修改 CAD 文件。
- `npm run check`、`npm run build`：检查组件身份、CAD 与网页哈希、文件结构和网页构建。

图纸更新继续沿用各设备 `scripts/drawing_geometry.py` 和现有图册生成流程，并核对实际页渲染。任何未执行的验证均保持待完成，不沿用历史通过状态。
