# Wii U 建模过程

原版白色 WUP-001 Basic 主机及 WUP-010 GamePad。每轮在 FreeCAD MCP 主线程中执行并保存检查点；历史轮次中的间隙问题由后续轮次修正。

## 01 · native_rounded_wup001_enclosure

按 172 × 268.5 × 46 mm 塑料主体建立原生圆角截面、长向拉伸、空心壳及上下分件，保留独立前面板和外伸脚垫。

[源码入口](scripts/iter01_native_rounded_wup001_enclosure.py) · [检查记录](output/reports/01_native_rounded_wup001_enclosure.json)

## 02 · front_disc_slot_controls_sd_and_dual_usb

加入吸入式光盘槽、电源与退盘控制、外露红色同步键，以及独立前门内的九接点 SD 卡座与双 USB 接口。

[源码入口](scripts/iter02_front_disc_slot_controls_sd_and_dual_usb.py) · [检查记录](output/reports/02_front_disc_slot_controls_sd_and_dual_usb.json)

## 03 · rear_hdmi_av_stacked_usb_and_cooling_grille

补齐背面 HDMI 十九接点、AV 十六接点、感应条与供电口，以及堆叠双 USB、三列排风格栅和两侧通风槽。

[源码入口](scripts/iter03_rear_hdmi_av_stacked_usb_and_cooling_grille.py) · [检查记录](output/reports/03_rear_hdmi_av_stacked_usb_and_cooling_grille.json)

## 04 · basic_mainboard_mcm_four_memories_and_emmc

加入 Basic 主板、CPU/GPU 多芯片载板、四片 DDR3L 与 8 GB eMMC 封装，补齐视频、系统及分区供电器件；内部电路布置明确作为学习近似。

[源码入口](scripts/iter04_basic_mainboard_mcm_four_memories_and_emmc.py) · [检查记录](output/reports/04_basic_mainboard_mcm_four_memories_and_emmc.json)

## 05 · underside_radio_modules_and_compatibility_memory

补齐主板背面的三块独立无线模块、屏蔽罩、微型同轴端口和兼容模式存储器，并调整两枚器件以消除与电容的干涉。

[源码入口](scripts/iter05_underside_radio_modules_and_compatibility_memory.py) · [检查记录](output/reports/05_underside_radio_modules_and_compatibility_memory.json)

## 06 · mcm_heatsink_axial_fan_and_offset_air_duct

加入多芯片封装的共用鳍片散热器、后部轴流风扇及原生剖面放样风道，保持散热层与外壳、端口和主板分离。

[源码入口](scripts/iter06_mcm_heatsink_axial_fan_and_offset_air_duct.py) · [检查记录](output/reports/06_mcm_heatsink_axial_fan_and_offset_air_duct.json)

## 07 · wiiu_slot_drive_pickup_and_pressed_cover

以共用传送机构原语建立 Wii U 吸入式光驱，重新确定机架尺寸、上盖加强筋和安装点，保留主轴、滚轮、齿轮及导轨光头。

[源码入口](scripts/iter07_wiiu_slot_drive_pickup_and_pressed_cover.py) · [检查记录](output/reports/07_wiiu_slot_drive_pickup_and_pressed_cover.json)

## 08 · shield_layers_support_columns_and_clearances

加入上下屏蔽板、主板和光驱支柱及机壳螺钉；修正无线接口罩和风道底部的实际装配间隙，避免螺柱超出圆角外形。

[源码入口](scripts/iter08_shield_layers_support_columns_and_clearances.py) · [检查记录](output/reports/08_shield_layers_support_columns_and_clearances.json)

## 09 · native_gamepad_curved_grips_and_touch_display

建立 GamePad 原生曲面前后壳、空心握柄和 6.2 英寸显示层，保留金属背板、LCD 支承、触摸层和黑色细边框的独立组件。

[源码入口](scripts/iter09_native_gamepad_curved_grips_and_touch_display.py) · [检查记录](output/reports/09_native_gamepad_curved_grips_and_touch_display.json)

## 10 · gamepad_dual_sticks_buttons_camera_and_nfc

补齐双摇杆、ABXY、十字键、START/SELECT、HOME 蓝色环、TV 和电源控制，加入前摄像头、红外窗口、NFC 标记及立体声开口。

[源码入口](scripts/iter10_gamepad_dual_sticks_buttons_camera_and_nfc.py) · [检查记录](output/reports/10_gamepad_dual_sticks_buttons_camera_and_nfc.json)

## 11 · gamepad_shoulders_battery_door_and_edge_ports

加入 L/R 与 ZL/ZR、可拆电池盖、音量滑块、耳机与充电端口、底部扩展口及充电触点，同时完善主机螺钉和风道的避让。

[源码入口](scripts/iter11_gamepad_shoulders_battery_door_and_edge_ports.py) · [检查记录](output/reports/11_gamepad_shoulders_battery_door_and_edge_ports.json)

## 12 · gamepad_boards_nfc_display_support_and_battery

补齐 GamePad 主板、无线和 NFC 模块、镂空显示支架、原版 1500 mAh 电池、独立按键板、相机、麦克风与立体声扬声器。

[源码入口](scripts/iter12_gamepad_boards_nfc_display_support_and_battery.py) · [检查记录](output/reports/12_gamepad_boards_nfc_display_support_and_battery.json)

## 13 · gamepad_analog_modules_button_domes_and_feedback

加入双模拟摇杆的回中弹簧、支承和电位器、按键硅胶与推杆、肩键小板及偏心振动机构，保留可独立查看的机械和电子组件。

[源码入口](scripts/iter13_gamepad_analog_modules_button_domes_and_feedback.py) · [检查记录](output/reports/13_gamepad_analog_modules_button_domes_and_feedback.json)

## 14 · gamepad_fixing_columns_battery_retainer_and_stylus

补齐 GamePad 外壳和主板固定点、电池盖螺钉与内部承托边框，并加入独立 WUP-015 触控笔学习模型。

[源码入口](scripts/iter14_gamepad_fixing_columns_battery_retainer_and_stylus.py) · [检查记录](output/reports/14_gamepad_fixing_columns_battery_retainer_and_stylus.json)

## 15 · speaker_select_and_shoulder_clearances

根据装配求交结果分开右扬声器与 SELECT 推杆，并同步调整扬声器开口；移开肩键小板，使其避让模拟摇杆电位器。

[源码入口](scripts/iter15_speaker_select_and_shoulder_clearances.py) · [检查记录](output/reports/15_speaker_select_and_shoulder_clearances.json)

## 16 · case_column_fit_and_native_surface_continuity

依据全装配求交移动下部螺柱并补齐按键板和支承框的通孔；保留壳体分段曲面以避免自动合并损坏曲线，并执行全部组件严格实体检查。

[源码入口](scripts/iter16_case_column_fit_and_native_surface_continuity.py) · [检查记录](output/reports/16_case_column_fit_and_native_surface_continuity.json)

## 17 · console_data_power_fan_and_radio_harnesses

加入主机光驱数据软排线、独立供电导线、后排风扇线束与三组无线模块天线线，并在屏蔽板和无线小板保留走线通道；接点数量与局部走线为学习近似。

[源码入口](scripts/iter17_console_data_power_fan_and_radio_harnesses.py) · [检查记录](output/reports/17_console_data_power_fan_and_radio_harnesses.json)

## 18 · gamepad_flex_cables_battery_audio_and_radio_wiring

加入显示、双侧按键、底部控制与 NFC 软排线，补齐电池、立体声扬声器、麦克风和无线天线连接；保留独立组件及显示支架通道，线数和局部路径为示意。

[源码入口](scripts/iter18_gamepad_flex_cables_battery_audio_and_radio_wiring.py) · [检查记录](output/reports/18_gamepad_flex_cables_battery_audio_and_radio_wiring.json)

## 19 · front_io_and_fan_harness_clearances

将光驱电源线移至前置接口之后并错层布线，避让 SD 卡座、USB 及前缘支柱；同步分层风扇线，消除导线之间的实体相交。

[源码入口](scripts/iter19_front_io_and_fan_harness_clearances.py) · [检查记录](output/reports/19_front_io_and_fan_harness_clearances.json)

## 20 · basic_console_and_gamepad_power_adapters

加入 Basic 套装的 WUP-002 主机电源和 WUP-011 GamePad 电源，分别绘制空心壳、线缆、日式插头、专用双接点端头及内部结构示意；适配器局部尺寸为照片近似。

[源码入口](scripts/iter20_basic_console_and_gamepad_power_adapters.py) · [检查记录](output/reports/20_basic_console_and_gamepad_power_adapters.json)

## 21 · gamepad_harness_fit_and_dual_hdmi_plugs

修正 GamePad 线束与螺柱、屏蔽罩和其他线束的间隙；加入 Basic 套装 HDMI 线、两端梯形金属插头、十九接点及带内孔的护线套。

[源码入口](scripts/iter21_gamepad_harness_fit_and_dual_hdmi_plugs.py) · [检查记录](output/reports/21_gamepad_harness_fit_and_dual_hdmi_plugs.json)

## 22 · final_connector_speaker_and_power_cord_fit

根据全部装配求交结果微调底部排线、扬声器引线与电源插头的终端路径，并对完整套装每个组件执行严格实体检查。

[源码入口](scripts/iter22_final_connector_speaker_and_power_cord_fit.py) · [检查记录](output/reports/22_final_connector_speaker_and_power_cord_fit.json)
