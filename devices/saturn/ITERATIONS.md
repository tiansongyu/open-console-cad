# Sega Saturn 建模过程

选择日版灰色 HST-3200。每轮在 FreeCAD MCP 主线程中执行并保存检查点，后续轮次逐步补齐内部和修正间隙。

## 01 · native_tapered_shell_and_raised_central_deck

按 HST-3200 灰色初代照片建立独立上下空心壳、倾斜侧肩与原生多截面抬高中央台；260 × 230 × 83 mm 仅作为近似学习包络，家族规格依据另行注明。

[源码](scripts/iter01_native_tapered_shell_and_raised_central_deck.py) · [记录](output/reports/01_native_tapered_shell_and_raised_central_deck.json)

## 02 · curved_disc_lid_well_and_rear_cartridge_bay

加入带弧形前缘的原生光驱盖、深光盘仓与光头通道、后部卡槽衬框及防尘门，补齐灰色初代的顶盖文字和深色弧形装饰。

[源码](scripts/iter02_curved_disc_lid_well_and_rear_cartridge_bay.py) · [记录](output/reports/02_curved_disc_lid_well_and_rear_cartridge_bay.json)

## 03 · curved_black_control_panel_and_blue_oval_keys

沿原生顶壳曲面分出深色控制面板，加入蓝色椭圆 POWER / RESET、中央 OPEN 键及双指示灯；按钮保留独立实体和外壳开孔。

[源码](scripts/iter03_curved_black_control_panel_and_blue_oval_keys.py) · [记录](output/reports/03_curved_black_control_panel_and_blue_oval_keys.json)

## 04 · dual_controller_ports_and_conformal_control_labels

补齐原版双手柄端口、绝缘载体与九位触点；将面板和按键文字投到实际曲面上，避免平面字片埋入斜面。接点尺寸为学习示意。

[源码](scripts/iter04_dual_controller_ports_and_conformal_control_labels.py) · [记录](output/reports/04_dual_controller_ports_and_conformal_control_labels.json)

## 05 · rear_mains_av_communication_and_service_cover

补齐上壳八字电源座、下壳 AV 与通信接口、独立后部电池扩展盖，以及侧面和底部通风槽；接口触点与局部尺寸保留学习近似说明。

[源码](scripts/iter05_rear_mains_av_communication_and_service_cover.py) · [记录](output/reports/05_rear_mains_av_communication_and_service_cover.json)

## 06 · va05_mainboard_dual_sh2_graphics_sound_and_memory

依据 MAIN VA0.5 拆解布局建立主板、双 SH-2、两组图形处理器、SCU、音频处理、系统管理与分区存储，并加入电容、时钟、无源件与线束插座；引脚和电路布局为学习近似。

[源码](scripts/iter06_va05_mainboard_dual_sh2_graphics_sound_and_memory.py) · [记录](output/reports/06_va05_mainboard_dual_sh2_graphics_sound_and_memory.json)

## 07 · separate_cd_subsystem_rear_coin_cell_and_cartridge_reader

加入原版独立 CD 子系统板、SH-1 与 CD 控制封装、缓存和支承，补齐后部可换 CR2032 电池、备份复位键及双面卡槽触点；局部引脚与连接尺寸为学习近似。

[源码](scripts/iter07_separate_cd_subsystem_rear_coin_cell_and_cartridge_reader.py) · [记录](output/reports/07_separate_cd_subsystem_rear_coin_cell_and_cartridge_reader.json)

## 08 · mainboard_socket_clearance_and_strict_glyph_geometry

移开主板电源插座以避让无源器件，并调整光驱支承孔；采用独立字形间距修复微小 CAD 文字的自交，对全部已建组件执行严格实体检查。

[源码](scripts/iter08_mainboard_socket_clearance_and_strict_glyph_geometry.py) · [记录](output/reports/08_mainboard_socket_clearance_and_strict_glyph_geometry.json)

## 09 · white_optical_supports_spindle_and_guided_pickup

加入四支白色长支座、独立光驱控制板、主轴与定位台、双导轨光头、螺旋进给件和电机，保留机架、固定件与光盘仓的装配间隙。

[源码](scripts/iter09_white_optical_supports_spindle_and_guided_pickup.py) · [记录](output/reports/09_white_optical_supports_spindle_and_guided_pickup.json)

## 10 · optical_connector_and_drive_gear_fit

根据装配求交避让光驱板固定螺钉，并补充进给齿轮的顶架开口；复查全部已建组件的严格实体有效性。

[源码](scripts/iter10_optical_connector_and_drive_gear_fit.py) · [记录](output/reports/10_optical_connector_and_drive_gear_fit.json)
