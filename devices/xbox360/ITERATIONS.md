# Xbox 360 建模迭代

全部轮次已在独立 FreeCAD 会话从空文档重建，组件几何、装配、STEP、图册与网页核验通过；公开部署证据另见报告。

| 轮次 | 阶段 | 内容 |
| --- | --- | --- |
| 01 | native_concave_white_enclosure | 根据原版白色 Xenon 外观建立独立的上下凹曲面壳和可拆前面板，均保留草图曲线与原生拉伸；309×258×83 mm 为暂定学习包络，局部曲率为照片指导近似。开孔、侧格栅、内部机构与无线控制器后续分轮加入。 |
| 02 | original_faceplate_doors_and_ring_of_light | 加工原版 DVD 托盘、双记忆单元门、双 USB 翻门、红外窗、配对与出盘键，建立独立电源键及四分区导光。Premium 镀铬托盘和细标识独立建模；门后插座和电子板后续补齐。 |
| 03 | perforated_end_grilles_and_shell_inlets | 加入左右独立灰色圆孔格栅，壳体两端三列圆孔为真实贯穿几何，补充横置橡胶支脚；孔距、数量和材料厚度按原机照片作结构学习近似。 |
| 04 | xenon_rear_ports_and_twin_fan_exhaust | 闭合后部原生曲面，加工外置 DC、原版 AV、叠置 LAN/USB 开口与双风扇排风圆孔；明确不加入后期 HDMI 接口。后部标识为 CAD 学习标识，不复制实机序列号。 |
| 05 | native_steel_chassis_and_board_supports | 建立带宽度表达式的原生金属底盘、折边、对齐后排风孔、前后接口通道及九组分离支承/紧固件。金属板厚、固定位置与间隙为学习近似；保留底盘尺寸和布尔加工历史。 |
| 06 | native_xenon_board_outline_and_mounting | 建立原生 Xenon 主板与后部双风扇凹口，保留九组机壳固定孔、CPU/GPU 独立夹具通道及安装焊盘。板外形和孔位为照片指导近似，不提供制造 Gerber 或实际电路。 |
| 07 | xenon_xenos_edram_and_double_sided_memory | 按原版主板照片分离 Xenon CPU、Xenos GPU 与同封装 eDRAM，加入主板正反各四枚 GDDR3 包络。焊球网格仅展示连接层，不宣称真实球数、引脚排列或生产封装尺寸。 |
| 08 | original_ana_southbridge_nand_and_io_logic | 加入原版 ANA 模拟视频编码器、系统桥、16 MB NAND 外形与独立成形引脚，补齐以太网、音频、系统管理和时钟器件。布局及封装为非功能性近似，明确不混入后期 HDMI/HANA 方案。 |
| 09 | original_regulator_coils_bulk_caps_and_passives | 加入右侧及后部供电器件，独立磁芯、绕组、圆柱电容、端子和功率封装；分布式小器件避开主芯片、孔位及接口。所有数量与电气连接仅为非功能性布局示意，不是原厂 BOM 或电路。 |
| 10 | original_memory_usb_lan_av_and_dc_connectors | 加入前双 USB、双记忆单元插座、后 LAN/USB、原版模拟 AV 和外置电源 DC 接口；屏蔽、绝缘、舌片与接点独立建模。接点排列和键位仅为结构示意，不可用于接线或制造配对插头。 |
| 11 | front_rf_board_ring_light_and_ir_controls | 分离前端 RF 板、屏蔽罩、四象限 LED 与导光柱、电源/配对触点及红外接收器。无线器件、天线和小板形状为结构示意，不提供射频设计或实际电路。 |
| 12 | original_cpu_tower_gpu_low_sink_and_x_clamps | 建立早期 CPU 立式鳍片、独立铜热管和低矮 GPU 铝鳍片，加入三块导热界面、支柱与背面 X 夹具；热管具有分离通道，明确不加入后期 GPU 延伸热管。局部尺寸、鳍片数量及夹具形状为照片指导近似。 |
| 13 | twin_rear_axial_fans_and_separate_motors | 加入双后置轴流风扇，分离开孔框架、扭转叶片、转子、轴、轴承、定子、线圈与驱动板；风扇内部为学习示意，叶片与厂家变体不作精确等同。 |
| 14 | original_white_open_bottom_air_shroud | 加入 CPU 与 GPU 两支白色开放底部导风罩，低支路预留上方 DVD 空间，后段抬升接近双风扇入口；分离卡扣与安装间隙。风道形状为装配关系示意，不提供热流性能结论。 |
| 15 | tray_loading_optical_drive_native_enclosure | 建立托盘式 DVD 光驱下盘、开口折边、可拆上盖、压筋、盖板螺钉及隔振支承。供应商光驱存在变体，本模型仅表示原版装配层次，不宣称特定型号的精确尺寸或内部 BOM。 |
| 16 | dvd_tray_spindle_blank_disc_and_pickup | 建立开槽光盘托盘、独立滑轨、空白 120 mm 介质、主轴电机/轴/轮毂、磁性夹盘、光头导杆与镜片。内部行程位置和机械细节为非功能性近似，不包含游戏内容。 |
| 17 | dvd_logic_loading_drive_and_flex_connections | 补齐光驱控制板与独立封装接点、托盘电机、皮带、齿轮与齿条、光头柔性线及后部 SATA/电源插座；传动齿形、数量和连线均为非功能性学习示意。 |
| 18 | removable_twenty_gigabyte_hdd_carrier_and_drive | 加入原版 Premium 可拆 20 GB 端部硬盘组件、镀铬嵌件、释放键/挂钩及内部 2.5 英寸盘体、独立盖板和控制板。外部硬盘会超出主机本体近似包络；外壳曲率和驱动器布局不代表制造规格。 |
| 19 | hard_drive_platter_actuator_and_removable_dock | 分离硬盘盘片、主轴、磁头执行器、音圈/磁体和连接软排，建立端部可拆接口及格栅贯通开口。磁盘数量、磁头和接点排列为结构示意，不代表原厂引脚定义、容量计算或存储数据。 |
| 20 | internal_dvd_rf_ir_fan_and_hdd_harnesses | 补齐光驱数据/电源、前端 RF/红外、双风扇与可拆硬盘内部线束，分离主板插座及接点，并加工绝缘导线的底盘/风罩通道。线色、芯数、路径和端点为静态结构示意，不提供真实电气接线。 |
| 21 | curved_upper_shield_case_fasteners_and_embossed_mark | 补齐原生曲面金属上屏蔽、对齐通风孔、独立机壳长紧固件/导向柱/卡扣及顺曲面排列的外壳字样。固定数量、位置和分离间隙为装配学习近似。 |
| 22 | wireless_controller_native_grip_shell_and_aa_bay | 建立白色无线控制器的上下原生曲线放样壳、分缝及背面双 AA 电池座开口。外形参考 Microsoft 同家族手柄规格和原版照片，曲率与内部间隙为学习近似；不混入后期变形十字键或 USB-C。 |
| 23 | original_asymmetric_sticks_fixed_dpad_abxy_and_guide | 加工原版非对称双摇杆、固定十字键、彩色 ABXY、Guide 四分区灯环、Back/Start 和肩键开口；独立按键、凹面拇指帽与触点凸粒分件表达，后续补齐摇杆、导电胶和扳机内部。 |
| 24 | early_wireless_controller_board_baseband_and_rf_module | 按 2005 年 FCC 样品建立原生主板、引脚式主控、分离射频子板/可拆屏蔽罩、晶振及电池/充电接点。主板与局部封装为学习近似，明确区别后续 WC01 无线芯片组改款；引脚数量不构成原厂电路。 |
| 25 | controller_split_contacts_and_separate_silicone_membranes | 补齐主板分离接点、ABXY/Guide/菜单共用导电胶与四方向独立胶垫，分别建立弹性锥壁、碳粒和十字键压力垫；保留接点与静止碳粒之间的间隙。该机构为静态结构学习，不模拟实际力学或电路。 |
| 26 | asymmetric_two_axis_joysticks_pots_and_click_switches | 补齐非对称双摇杆的金属笼架、双轴万向支架、球轴、电位器壳/转子/电阻轨道/滑片和按下开关，加入独立弹簧、穿板端子及拇指帽颈部轴孔。机构尺寸与轨道为学习近似。 |
| 27 | early_white_triggers_black_brackets_return_springs_and_pots | 加入原版白色扳机、早期黑色支架、独立轴与回位线圈、扳机电位器内部件和穿板端子，补齐肩键触点及传力柱；机构参考 2005 年样品，不用后期黑色手柄的白色支架代替。 |
| 28 | unequal_rumble_motors_and_removable_two_aa_holder | 加入两只不同尺寸的偏心振动电机及分离转子、磁体、线圈、轴、配重和双线接口；补齐可拆 AA 电池座、两枚反向安装的 LR6 电池、释放键与独立弹簧/触片。电机内部和电池接触堆叠为非功能性结构示意。 |
| 29 | original_charge_headset_ports_gray_trim_and_seven_fasteners | 补齐原版充电/配对、2.5 mm 耳机与扩展接口、分离灰色握柄嵌件、七处背面六瓣防拆紧固件及示意小器件。接口接点仅表达结构，未加入原套装没有的 Windows 接收器、USB 线或充电电池包。 |
| 30 | ribbed_203w_power_brick_shell_and_status_indicator | 建立原版 203W 外置电源的可编辑双半壳、横向散热肋、端部通风、四处紧固、AC/DC 开口及独立状态灯；约 75 × 215 × 55 mm 外壳和内部安装尺寸为学习近似，不冒充厂商尺寸。 |
| 31 | 203w_supply_board_shields_transformer_and_heat_sinks | 补齐 203W 原版级别的电源板、上下屏蔽、分离磁芯/绕组、大电容和散热器。依据原版分析确认强制风冷架构；内部排布和器件数量为明确标注的非功能结构示意，不复制 175W 后期板型。 |
| 32 | power_brick_blower_grounded_inlet_and_captive_dc_output | 补齐外置电源的独立微型风机内部件、三位接地 AC 入口、固定式输出电缆与早期专用 DC 插头。微型风机和八位端子布局为非功能示意，展示线长缩短，不提供接线或电源制造说明。 |
| 33 | original_single_ear_headset_and_controller_volume_adapter | 依据 2005 安装手册补齐单耳头戴耳机、独立扬声器内部件、可调麦克风和原版手柄端音量/静音适配器。区分 2007 手册中的后期小插头版本；内部音频结构与局部曲率均为学习示意。 |
| 34 | original_component_hd_av_six_rca_optical_and_tv_selector | 补齐原配六 RCA Component HD AV 线，分离 Y/Pb/Pr、黄色复合视频和红白音频，保留宽 AV 端、TV/HDTV 选择器与 Toslink 光纤口。接点布局和线长为展示近似，不混入后期 HDMI 或五 RCA 改款。 |
| 35 | bundled_ethernet_and_north_american_grounded_ac_cord | 补齐原配网线的双端八触点与独立包胶/卡扣，选择北美三脚接地电源线版本；地区范围明确，不加入北欧 SCART、第二根区域电源线或限时赠送遥控器。电缆为缩短展示长度。 |
