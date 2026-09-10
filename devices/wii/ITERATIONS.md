# Wii CAD iterations

The RVL-001 study includes fifteen source stages and a complete CAD, drawing and web delivery. Local details and internals are approximate.

| Stage | Source | Work |
| --- | --- | --- |
| 01 | [iter01](scripts/iter01_native_white_enclosure_and_separate_faceplate.py) | 建立初代白色 RVL-001 的原生草图、拉伸与圆角外壳，独立前面板及四个横放脚垫；按 157 × 215.4 × 44 mm 横放坐标建模。 |
| 02 | [iter02](scripts/iter02_blue_disc_slot_controls_sd_and_sync.py) | 加入真实贯穿的吸入式光盘槽、蓝色导光件、独立电源与重置/退盘键、前门、九接点 SD 卡座及红色同步键。 |
| 03 | [iter03](scripts/iter03_rear_usb_multi_av_sensor_and_power.py) | 补齐双 USB、十六位 Multi AV、感应条和直流电源接口的独立触点及背部排气格栅，同时细化前面板电源/退盘符号。 |
| 04 | [iter04](scripts/iter04_gamecube_four_ports_two_cards_and_side_doors.py) | 加入初代特有的四个六接点 GameCube 手柄接口、两个十二接点存储卡槽及独立侧盖，补齐相对侧的进气孔。 |
| 05 | [iter05](scripts/iter05_mainboard_broadway_hollywood_memory_and_power.py) | 加入主板、Broadway/Hollywood 封装、存储器、视频编码和分区电源器件，保留光驱与无线模块连接器；内部布置及互连数量明确作为学习近似。 |
| 06 | [iter06](scripts/iter06_finned_heatsink_rear_fan_and_wireless_modules.py) | 加入共用铝制鳍片散热器、七叶后排风扇、独立 Wi-Fi 与蓝牙模块及屏蔽罩，留出后部接口与光驱的装配空间。 |
| 07 | [iter07](scripts/iter07_slot_loading_drive_pickup_gears_and_clamp.py) | 建立吸入式光驱的底架、双滚轮、齿轮、主轴与压盘件，并加入双导轨光头、螺旋进给丝杆和独立光驱控制板。 |
| 08 | [iter08](scripts/iter08_layered_shields_fixings_and_fan_clearances.py) | 补齐上下屏蔽板、主板与光驱支柱和机壳螺钉；通过主板后缘缺口及无线板位置调整消除风扇与支柱干涉。 |
| 09 | [iter09](scripts/iter09_original_rvl003_remote_shell_and_controls.py) | 建立原版 RVL-003 遥控器的曲面后壳、正面按键、红外窗口、扬声器孔、四个指示灯、背部 B 键和六接点扩展接口，不加入 MotionPlus 外形。 |
| 10 | [iter10](scripts/iter10_remote_optical_sensor_speaker_rumble_and_aa_cells.py) | 补齐遥控器控制板、红外相机、三轴加速度计、扬声器、偏心振动机构、两节 AA 电池及弹簧触点，加入按键导电接点和 B 键小板。 |
| 11 | [iter11](scripts/iter11_curved_nunchuk_controls_and_expansion_cable.py) | 加入原生贝塞尔轮廓的 Nunchuk 曲面外壳、模拟摇杆、C/Z 键、控制板与扩展线；同时按干涉报告调整主机外壳支柱与无线接口周边间隙。 |
| 12 | [iter12](scripts/iter12_original_sensor_bar_and_vertical_stands.py) | 加入原版双五灯感应条、两芯插头与感应条支架，并用原生斜面草图和拉伸制作竖放支架，补齐辅助底板。 |
| 13 | [iter13](scripts/iter13_power_adapter_av_connections_and_blank_media.py) | 加入原版电源适配器的结构示意、日式电源插头、双芯直流插头、十六位 AV 转三 RCA 线，以及不含游戏数据的 12 cm 与 8 cm 空白光盘。 |
| 14 | [iter14](scripts/iter14_harness_antenna_case_bosses_and_final_fit.py) | 补齐光驱排线与供电线、前灯和风扇线束、两条 Wi-Fi 天线线及遥控器/双节棍三翼螺钉，修正小板与接点间隙，并打开主机前缘的光盘与走线通道。 |
| 15 | [iter15](scripts/iter15_verified_routing_and_strict_brep_final_fit.py) | 依据全装配求交结果移动双节棍前固定点、避让光驱支柱并分开前灯线束的转弯高度，逐一执行全部组件的严格 BRep 检查。 |
