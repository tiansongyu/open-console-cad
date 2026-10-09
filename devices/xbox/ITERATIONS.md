# 原版 Xbox · 十八轮建模记录

代表版本为 2001 年黑色 v1.0 主机与原版有线 Duke；每轮保留原生工程、实体检查及预览。

| 轮次 | 工作内容 | 组件 | 检查记录 |
|---|---|---:|---|
| 01 | 采用微软明确标作近似的 320×260×100 mm 包络，建立可编辑下壳、独立前后面板、上盖及四个橡胶脚；局部壁厚和曲率为照片指导近似。 | 8 | [实体与来源](output/reports/01_original_black_enclosure_and_four_feet.json) |
| 02 | 补齐原版顶部宽 X 形筋、绿色圆形饰牌、侧面竖向通风槽和顶盖三角格栅、左侧 DVD 托盘面、中央退碟键与电源键；饰牌为静态结构，不含现代显示屏。 | 16 | [实体与来源](output/reports/02_raised_x_green_jewel_side_vents_and_front_controls.json) |
| 03 | 加入四个原版前控制器口及独立触点、后以太网、专用 A/V 与交流电源入口，并建立后置风扇通风孔；不混用 HDMI 或现代 USB 接口。 | 71 | [实体与来源](output/reports/03_four_original_controller_ports_and_rear_connections.json) |
| 04 | 建立上下冲压 EMI 屏蔽、折边与主板隔柱；上盖通风孔为照片指导的结构近似，所有隔柱和板件独立可查。 | 84 | [实体与来源](output/reports/04_lower_and_upper_emi_shields_and_board_posts.json) |
| 05 | 加入 v1.0 主板、733 MHz 处理器与 NV2A/MCPX 封装示意；四枚已装内存分布两面，同时保留空焊位，避免把空焊位误当成内存升级。 | 178 | [实体与来源](output/reports/05_original_v1_motherboard_cpu_gpu_mcpx_and_four_ram.json) |
| 06 | 补充圆柱电容、环形电感、离散封装、40 针并行 ATA 插座、主板供电插座及早期前控制器小板；元件数量、引脚及线路不构成可用电路。 | 544 | [实体与来源](output/reports/06_v1_regulators_board_discretes_and_parallel_ata_header.json) |
| 07 | 建立早期原版的大 CPU 被动散热器、小 GPU 主动散热器与后排风扇，避免混用后期无 GPU 风扇的修订；叶形、导热层和压片仅为结构近似。 | 611 | [实体与来源](output/reports/07_passive_cpu_active_v1_gpu_and_rear_exhaust.json) |
| 08 | 加入原版右侧开放式内置电源板、绝缘片、变压器、电容和散热片；几何仅用于布局观察，不构成电气安全或功能电路设计。 | 643 | [实体与来源](output/reports/08_open_internal_power_supply_board_and_magnetics.json) |
| 09 | 建立独立塑料光驱托架、金属罩、空载滑出托盘、主轴、光学滑架、导轨、齿轮、控制板及并行 ATA/供电插座；没有现代吸入式机构。 | 666 | [实体与来源](output/reports/09_original_dvd_carrier_tray_spindle_and_pickup.json) |
| 10 | 加入独立 3.5 英寸硬盘托架、铸壳、可拆顶盖、盘片、主轴和磁头臂示意；标签不伪造序列号，实体结构不表达实际可用容量。 | 683 | [实体与来源](output/reports/10_original_hard_drive_carrier_casting_platter_and_actuator.json) |
| 11 | 加入共享并行 ATA 折叠排线、硬盘/光驱电源束、GPU 与后风扇导线和前部控制线；所有线路为独立可检查的非功能路线近似。 | 711 | [实体与来源](output/reports/11_folded_shared_ide_ribbon_and_separate_power_harnesses.json) |
| 12 | 补齐四脚与两处标签下的六枚长壳体紧固件、主板螺钉及通用识别标记；驱动槽和螺纹简化，不伪造序列号或监管认证。 | 748 | [实体与来源](output/reports/12_six_hidden_case_screws_board_fasteners_and_labels.json) |
| 13 | 依据原版 Duke 实物建立宽大曲线放样前后壳、双层记忆卡口与静态绿色饰窗；不采用现代复刻 LCD、无线、电池或 Share 部件。 | 754 | [实体与来源](output/reports/13_original_duke_native_curved_shell_and_static_jewel.json) |
| 14 | 加入原版六键 White/Black/Y/B/X/A、非对称摇杆、圆盘十字键及 Start/Back；按键颜色、曲率和文字用几何近似表达。 | 776 | [实体与来源](output/reports/14_duke_six_original_face_keys_asymmetric_sticks_and_dpad.json) |
| 15 | 建立原版单主板、中央接口开口、控制芯片、晶振及两组带框架/万向支架/电位器的摇杆；封装和离散器件为结构研究近似。 | 835 | [实体与来源](output/reports/15_duke_single_mainboard_and_analog_mechanisms.json) |
| 16 | 补齐原版独立碳接点膜、无导电粒的六键硅胶层、自成一体的六胶碗十字键机构、Start/Back 胶件及双层记忆卡插座；不把后代双板结构移植到 Duke。 | 912 | [实体与来源](output/reports/16_duke_carbon_sheet_silicone_dpad_and_memory_slots.json) |
| 17 | 补充两枚不等偏心块握把电机、PH 接头导线、模拟扳机及压缩回位弹簧、七组壳体固定件；扳机和弹簧按原版结构重构，不表达寿命或力学性能。 | 953 | [实体与来源](output/reports/17_duke_dual_motors_analog_trigger_springs_and_screws.json) |
| 18 | 完成原版 Duke 有线线缆、可分离接头、专用主机插头及独立复合视频/左右声道 RCA 与交流线缆；墙端仅为通用示意，不指定地区插脚或认证。 | 978 | [实体与来源](output/reports/18_wired_duke_breakaway_composite_av_and_ac_accessories.json) |

最终交付包含完整与爆炸原生工程、三份 STEP、组件 CSV、十二页 A3 图册、原生图纸和二十二个网页视图。完整重建从空白文档执行十八轮，逐件对比保存工程；验收同时覆盖严格实体、装配求交、STEP 回读与参数修改复原。所有尺寸与电路边界见 [资料说明](references/SOURCES.md)。
