# 3DS 建模迭代

每轮由 FreeCAD 源码构建，组件数与检查结果来自对应报告。历史二进制检查点可通过重建宏重新生成。

| 轮次 | 内容与报告 | 组件 |
| --- | --- | ---: |
| 01 | [建立原生草图、凸台和圆角驱动的下机身、空腔、控制面板与分型缝。](output/reports/01_lower_enclosure.json) | 4 |
| 02 | [建立铰链套、通轴和轴承垫，加入上下 LCD、金属背板、下屏触控层及上屏立体显示膜层。](output/reports/02_dual_displays_and_hinge.json) | 22 |
| 03 | [完成圆形滑控钮、十字键、ABXY、SELECT/HOME/START 和电源键，各按键与安装孔分离建模。](output/reports/03_circle_pad_and_controls.json) | 50 |
| 04 | [加入充电插孔与底座触点、卡槽与 17 触点、红外窗、触控笔入口、耳机孔、指示灯和侧面开关。](output/reports/04_connectors_and_card_slots.json) | 82 |
| 05 | [增加两组五孔扬声器、内侧摄像头和双外摄像头、3D 强度滑块及麦克风入口。](output/reports/05_stereo_cameras_speakers_and_3d_slider.json) | 101 |
| 06 | [补齐后盖、带电池开口的支承板、固定螺钉、防滑垫、L/R 肩键及独立伸缩触控笔。](output/reports/06_rear_cover_and_stylus.json) | 121 |
| 07 | [加入竖置 CTR-003 电池、内层电芯、定位托架、三端接点及后部支承肋，按拆解布局保留电池开口。](output/reports/07_battery_and_rear_support.json) | 135 |
| 08 | [建立带缺口的主板、ARM/RAM/NAND 和电源音频封装、独立 Wi-Fi/红外/SD 模块，以及可分辨的阻容器件和端帽。](output/reports/08_mainboard_and_daughterboards.json) | 227 |
| 09 | [补齐滑控钮机构、硅胶按键与导电接点、三摄像头小板、扬声器/显示排线及穿过空心铰链的卷绕排线。](output/reports/09_control_mechanisms_and_flex.json) | 272 |
| 10 | [建立主板孔与支柱、上下层紧固件、上屏安装柱、EMI 屏蔽片、麦克风组件和显示缓冲垫。](output/reports/10_fasteners_shielding_and_mounts.json) | 305 |
| 11 | [按实体求交结果调整铰链轴与上盖旋转空间，修正肩键、卡槽、滑块、电池、主板、排线和安装件配合。](output/reports/11_verified_interface_refinement.json) | 305 |
| 12 | [完成剩余接触面修正、摄像头镜筒、合盖缓冲垫，以及原款 3DS 的被动触点充电底座示意。](output/reports/12_service_details_and_charging_cradle.json) | 324 |
| 13 | [完成底座后支承座与充电弹片配合，保存可复现的铰链轴参数，准备最终原生文件与图纸。](output/reports/13_cradle_contact_fit.json) | 324 |
