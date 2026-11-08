# Nintendo Switch 迭代源码

| 轮次 | 源码 |
|---|---|
| 01 | [iter01_tablet_enclosure.py](scripts/iter01_tablet_enclosure.py) |
| 02 | [iter02_display.py](scripts/iter02_display.py) |
| 03 | [iter03_ports_rails.py](scripts/iter03_ports_rails.py) |
| 04 | [iter04_rear_details.py](scripts/iter04_rear_details.py) |
| 05 | [iter05_joycon_shells.py](scripts/iter05_joycon_shells.py) |
| 06 | [iter06_sticks_buttons.py](scripts/iter06_sticks_buttons.py) |
| 07 | [iter07_shoulders_rail_controls.py](scripts/iter07_shoulders_rail_controls.py) |
| 08 | [iter08_tablet_internals.py](scripts/iter08_tablet_internals.py) |
| 09 | [iter09_joycon_internals.py](scripts/iter09_joycon_internals.py) |
| 10 | [iter10_dock_accessories.py](scripts/iter10_dock_accessories.py) |
| 11 | [iter11_clearance_refinement.py](scripts/iter11_clearance_refinement.py) |
| 12 | [iter12_final_fits.py](scripts/iter12_final_fits.py) |
| 13 | [iter13_verified_clearances.py](scripts/iter13_verified_clearances.py) |
| 14 | [iter14_strap_lock_seating.py](scripts/iter14_strap_lock_seating.py) |
| 15 | [iter15_exterior_refinement.py](scripts/iter15_exterior_refinement.py) · 外轮廓、曲面、肩键和控制布局 |
| 16 | [iter16_exterior_fits.py](scripts/iter16_exterior_fits.py) · 曲面装配配合与前面板细节 |
| 17 | [iter17_public_reference_edges.py](scripts/iter17_public_reference_edges.py) · 不等宽外缘曲面、保留内腔与 7.6 mm 面键 |
| 18 | [iter18_control_proportions.py](scripts/iter18_control_proportions.py) · HOME、截图键与字形比例，SL/SR、SYNC 和玩家灯位置校准 |

运行重建宏会依次生成各阶段模型。本次第 18 轮交付从第 17 轮已保存模型更新，未重跑全部阶段。原始设计说明和本版检查范围见设备 README 与 output/reports/control_delivery_checks.json。

第 19 轮：[microSD 标称外形与保存几何修复](scripts/iter19_microsd_nominal_geometry.py)。补齐卡片厚度、齐平接点与防误插轮廓，修复重叠字形、扬声器布尔精化及绕组连续性；四个曲面壳的严格检查问题保留在交付记录中。第 15 轮的肩键/红外旋转轴也已明确写入源码，重建不再依赖先前会话变量。
