# Nintendo DS NTR-001 · 建模迭代

每轮以独立源码入口执行；阶段二进制检查点保存在本地，可通过重建宏重新生成。最终发布使用最后一轮修正后的模型。

| 轮次 | 内容 | 组件数 | 预览 |
| --- | --- | ---: | --- |
| 01 | 按 NTR-001 初代厚机身建立银色下壳、主框架、控制面板、原生尺寸约束与内部空腔。 | 4 | [效果图](output/previews/01_ntr001_deep_enclosure_hero.png) |
| 02 | 建立两块 3 英寸 4:3 屏幕、黑色边框、下屏触控层及中央分段铰链，保留独立上盖结构。 | 23 | [效果图](output/previews/02_equal_displays_and_hinge_hero.png) |
| 03 | 加入初代凹入式控制区域、十字键、ABXY、左上电源键及右上 SELECT/START，按钮和安装孔分别建模。 | 49 | [效果图](output/previews/03_recessed_controls_hero.png) |
| 04 | 建立 Slot-1 与 17 触点、前方 Slot-2 导槽与 32 针 GBA 接口、专用充电口、耳机/附件口及前置音量滑块。 | 110 | [效果图](output/previews/04_ds_and_gba_slots_hero.png) |
| 05 | 增加双扬声器孔阵列、四个上盖螺钉垫、下机身麦克风、状态灯与 L/R 肩键；保留初代无摄像头结构。 | 130 | [效果图](output/previews/05_speakers_microphone_and_shoulders_hero.png) |
| 06 | 完成独立电池仓盖、七枚后壳螺钉、机型标识、触控笔收纳导管及约 75 mm 的初代非伸缩触控笔。 | 145 | [效果图](output/previews/06_battery_hatch_and_original_stylus_hero.png) |
| 07 | 建立 NTR-003 电池外壳、内部电芯、定位边、三端接点与容量标识，并补充后壳定位肋。 | 159 | [效果图](output/previews/07_ntr003_battery_hero.png) |
| 08 | 建立 NTR 主板轮廓、ARM9/ARM7/RAM 与电源音频封装、独立射频子板和屏蔽罩，按功能区域布置阻容器件。 | 235 | [效果图](output/previews/08_dual_arm_mainboard_and_rf_hero.png) |
| 09 | 加入独立按键胶垫、导电粒和主板触点，系统键/肩键开关、麦克风、指示灯，以及双屏排线和中空铰链内的卷曲排线段。 | 290 | [效果图](output/previews/09_button_membranes_and_display_flex_hero.png) |
| 10 | 补齐主板定位柱与紧固螺钉、上盖四处螺钉塔、下屏金属承托边和主封装屏蔽板，进入实体配合检查。 | 314 | [效果图](output/previews/10_mounts_and_lcd_carrier_hero.png) |
| 11 | 依据独立实体求交修正上盖旋转空间、按键通孔、双卡槽安装面、螺钉柱对齐、触控笔导管和排线出口。 | 314 | [效果图](output/previews/11_hinge_and_service_interface_fit_hero.png) |
| 12 | 完成剩余螺钉与支承肋配合、齐平附件触点、上盖与肩键标识、充电触点及音量滑块纹理，保存铰链轴参数。 | 321 | [效果图](output/previews/12_final_service_details_hero.png) |
| 13 | 校正合盖后上盖标识的阅读方向，并完成 L/R 薄层标识与机壳边缘的最后配合检查。 | 321 | [效果图](output/previews/13_cover_marking_and_final_fit_hero.png) |
| 14 | 将铰链处薄分型条改为直端退让轮廓，避免圆柱相切薄片在 STEP 回读修复时发生几何偏差。 | 321 | [效果图](output/previews/14_step_stable_parting_strip_hero.png) |
| 15 | 将下机身铰链开孔限定在中央铰链范围，恢复两侧连续壳体，修正网页视角中主板外露的问题。 | 321 | [效果图](output/previews/15_central_hinge_enclosure_hero.png) |
