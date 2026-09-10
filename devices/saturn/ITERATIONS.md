# Sega Saturn 建模过程

选择日版灰色 HST-3200。每轮通过 FreeCAD MCP 主线程执行，历史轮次的间隙和曲面问题由后续轮次修正。

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

## 11 · upper_housing_psu_transformer_and_power_switch

加入初代 HST-3200 的上壳电源板、变压器、滤波与散热器件、支承框和锁定电源开关，保留独立市电端头与线束；内部器件尺寸与电路为结构学习示意。

[源码](scripts/iter11_upper_housing_psu_transformer_and_power_switch.py) · [记录](output/reports/11_upper_housing_psu_transformer_and_power_switch.json)

## 12 · layered_shields_case_columns_and_board_fixings

加入上下屏蔽板、通风与维修开口、手柄端口压条、上下壳螺柱和主板承托，保留螺钉、橡胶脚垫及板件的独立避让。

[源码](scripts/iter12_layered_shields_case_columns_and_board_fixings.py) · [记录](output/reports/12_layered_shields_case_columns_and_board_fixings.json)

## 13 · native_lid_hinges_return_spring_and_sector_gears

加入光驱盖原生轴耳、钢轴、回位弹簧、扇形齿轮与小齿轮及金属支架，保留屋面与轴承间隙；机构用于结构观察，不代表经过验证的运动仿真。

[源码](scripts/iter13_native_lid_hinges_return_spring_and_sector_gears.py) · [记录](output/reports/13_native_lid_hinges_return_spring_and_sector_gears.json)

## 14 · single_cartridge_door_lid_latch_and_control_boards

按初代拆解修正整片卡槽防尘门，加入轴销与回位弹簧；补齐光驱盖锁扣、开盖导向、门检测开关、复位键及分立指示灯板和导光件。

[源码](scripts/iter14_single_cartridge_door_lid_latch_and_control_boards.py) · [记录](output/reports/14_single_cartridge_door_lid_latch_and_control_boards.json)

## 15 · lid_journal_bracket_and_disc_well_clearances

依据装配检查为固定轴承开出盖板内部避让，降低齿轮支架和固定件，并调整光盘仓角部的支承间隙，保持外表面轮廓。

[源码](scripts/iter15_lid_journal_bracket_and_disc_well_clearances.py) · [记录](output/reports/15_lid_journal_bracket_and_disc_well_clearances.json)

## 16 · original_grey_hss0101_controller_shell_and_six_keys

建立原版灰色 HSS-0101 手柄的原生曲线前后壳、圆盘十字键、黑色 ABC、蓝色 XYZ / START 和肩键，并补齐主机前部锁扣的光盘仓避让。

[源码](scripts/iter16_original_grey_hss0101_controller_shell_and_six_keys.py) · [记录](output/reports/16_original_grey_hss0101_controller_shell_and_six_keys.json)

## 17 · controller_board_silicone_inputs_and_five_fixings

补齐原版手柄的电路板、三组硅胶膜、碳膜接点、I/O 器件、肩键微动开关与五处外壳固定；同时完善主机灯板螺孔及卡槽防尘门轴孔。

[源码](scripts/iter17_controller_board_silicone_inputs_and_five_fixings.py) · [记录](output/reports/17_controller_board_silicone_inputs_and_five_fixings.json)

## 18 · console_harnesses_folded_ribbons_and_controller_cord

加入主机供电、光驱排线、指示灯、门检测和复位线束及屏蔽通道，补齐手柄九芯线、护线套和原始矩形插头；展示走线与线数不定义原厂电路。

[源码](scripts/iter18_console_harnesses_folded_ribbons_and_controller_cord.py) · [记录](output/reports/18_console_harnesses_folded_ribbons_and_controller_cord.json)

## 19 · controller_fit_original_ac_av_cords_and_blank_disc

调整盖板固定与手柄硅胶边界，补齐原版形式的日式电源线、八字端头、十接点 AV 转三 RCA 线及空白 12 cm 光盘，保留独立配件和组件编号。

[源码](scripts/iter19_controller_fit_original_ac_av_cords_and_blank_disc.py) · [记录](output/reports/19_controller_fit_original_ac_av_cords_and_blank_disc.json)

## 20 · separated_harness_routes_and_preserved_trim_surfaces

按装配求交分开灯板、门检测、复位和电源开关线束，调整相应通孔，并保留卡槽衬框和上壳的原始修剪曲面；全部已建组件执行严格实体检查。

[源码](scripts/iter20_separated_harness_routes_and_preserved_trim_surfaces.py) · [记录](output/reports/20_separated_harness_routes_and_preserved_trim_surfaces.json)

## 21 · continuous_lid_pilots_and_native_membrane_boundary

贯通铰链支承与支架固定孔，采用原生求交限制硅胶膜边界，使后续重算仍保留真实间隙，并复查全部组件的严格实体有效性。

[源码](scripts/iter21_continuous_lid_pilots_and_native_membrane_boundary.py) · [记录](output/reports/21_continuous_lid_pilots_and_native_membrane_boundary.json)

## 22 · power_switch_bend_final_clearance

移开第二根电源开关线与第一根下降弯管的局部相交，保留端头位置及相邻板件间隙。

[源码](scripts/iter22_power_switch_bend_final_clearance.py) · [记录](output/reports/22_power_switch_bend_final_clearance.json)
