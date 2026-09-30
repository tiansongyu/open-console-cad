# PS4 逐轮记录

当前为建模中间态，尚未完成整套交付。

| 轮次 | 内容 | 组件数 |
| --- | --- | --- |
| 01 | 原生斜面上下壳、亮面硬盘盖、中框、脚垫和灯条 | 8 |
| 02 | 吸入式光盘入口、双 USB 3.0、触控条及标识 | 56 |
| 03 | 后部 HDMI / 光纤 / LAN / AUX / AC、真实通风开口 | 111 |
| 04 | 原生硬盘壳体、盘片示意、SATA、独立托架与固定件 | 162 |
| 05 | 原生 L 形主板、APU、双面显存与主要逻辑 | 238 |
| 06 | 原生上下屏蔽板、固定件与显存导热垫 | 272 |
| 07 | 离心叶轮、风道、APU 接触层、热管与鳍片 | 334 |
| 08 | 内置电源壳体、原生电源板与滤波元件 | 374 |
| 09 | 安装层高调整、原生光驱框架、主轴与空白介质 | 387 |
| 10 | 光头、导杆、进给轴系与前部吸入滚轮 | 419 |
| 11 | 独立原生光驱控制板、逻辑与排线接口 | 484 |
| 12 | 光驱及光头排线、连接器与板料穿越通道 | 532 |
| 13 | 风扇及光驱电机线束、主板供电铜排与通道 | 553 |
| 14 | 硬盘托架固定、主板 SATA 插座及独立接点 | 602 |
| 15 | 后壳防拆螺钉、安装柱及型号标识 | 609 |
| 16 | DualShock 4 原生曲面上下壳、摇杆杯与触摸板开口 | 611 |
| 17 | 触摸板、方向键、符号按键、PS 键与凹面摇杆帽 | 630 |
| 18 | 原生控制器主板、双轴摇杆、电位器与主要逻辑 | 704 |
| 19 | 按键接点膜、硅胶回弹穹顶与扬声器 | 734 |
| 20 | 肩键、扳机、轴系与弹簧；补齐主板穿过摇杆杯的通道 | 756 |
| 21 | 电池、托架、双振动电机和引线；修正扳机装配间隙 | 788 |
| 22 | 初代后灯条、充电小板、Micro-USB、耳机与 EXT 口 | 823 |
| 23 | 充电、触摸与按键排线，扬声器引线及通道 | 890 |
| 24 | 四组控制器固定柱与螺钉、触摸按下机构、型号标识 | 899 |

| 25 | 时钟电池固定、触控电极、灯条板与 AC 内部连接 | 921 |
| 26 | 光驱装载电机、三级齿轮、支承与线束 | 935 |
| 27 | 电源线与双端十九接点 HDMI 线 | 990 |
| 28 | USB-A 四接点至 Micro-B 五接点充电线 | 1010 |
| 29 | 单耳扬声器、MIC 滑动开关、独立线夹与四段插头 | 1039 |

[当前原生工程](output/PlayStation4_Study.FCStd) · [打开宏](Open_PlayStation4.FCMacro) · [重建已实现阶段](Rebuild_PlayStation4.FCMacro)

原生几何通过 FreeCAD MCP GUI 线程生成。实体交集检查保存在 `output/reports/stageNN_interference.json`；完整源码重建、STEP 和图纸验收在模型完成后执行。

前六轮从源码独立重建，272 个组件逐件几何比对通过：[重建记录](output/reports/stage06_rebuild.json)。

前七轮全部 334 个组件通过严格 BRep 检查与源码重建几何比对：[严格检查](output/reports/stage07_strict_bop.json) · [重建比对](output/reports/stage07_rebuild.json)。

前十轮全部 419 个组件通过严格 BRep、767 组装配候选求交和独立源码重建几何比对：[严格检查](output/reports/stage10_strict_bop.json) · [装配检查](output/reports/stage10_interference.json) · [重建比对](output/reports/stage10_rebuild.json)。

前十四轮 602 个组件的 1,356 组装配候选全部求交通过：[装配检查](output/reports/stage14_interference.json)。

前十四轮全部 602 个组件的严格 BRep 和独立源码重建比对通过：[严格检查](output/reports/stage14_strict_bop.json) · [重建比对](output/reports/stage14_rebuild.json)。

第十五轮 609 个组件的 1,361 组装配候选全部通过：[装配检查](output/reports/stage15_interference.json)。

第十七轮 630 个组件的 1,378 组装配候选全部通过：[装配检查](output/reports/stage17_interference.json)。第十八、十九轮检查记录了一处主板与后壳摇杆杯上缘的穿插；第二十轮新增真实板料通道解决该问题，后续以修正后的装配检查为准。

第二十一轮 788 个组件的 1,729 组装配候选全部通过：[装配检查](output/reports/stage21_interference.json)。该版本已消除第十八至二十轮历史检查记录中的主板边缘、扳机、接点膜载体及轴端穿插。

第二十二轮 823 个组件、1,796 组装配候选通过；第二十三轮 890 个组件、1,900 组候选通过：[接口检查](output/reports/stage22_interference.json) · [排线检查](output/reports/stage23_interference.json)。第二十四轮全部 899 个组件通过严格 BRep：[严格检查](output/reports/stage24_strict_bop.json)。

第二十四轮 899 个组件的全部 2,046 组装配候选通过：[装配检查](output/reports/stage24_interference.json)。控制器部分和主机现有装配均无已知实体穿插；完整交付仍待末端结构、附件和最终验收。

第二十五至二十八轮分别通过 2,096、2,142、2,189、2,204 组装配候选求交检查，报告保存在对应 `stageNN_interference.json`。

第二十九轮 1,039 个组件通过严格 BRep 和全部 2,225 组装配候选求交：[严格检查](output/reports/stage29_strict_bop.json) · [装配检查](output/reports/stage29_interference.json)。MIC 推杆通道与线夹下方线缆路径的穿插已修正，完整源码重建和交付文件验收继续进行。
