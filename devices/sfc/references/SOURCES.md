# Super Famicom 原始资料与建模边界

选择日版 SHVC-001 / 早期 SHVC-CPU-01，保留独立 SHVC-SOUND 声音模块。控制器选用 SHVC-005，内部依据标注 1992 的原版 PCB；不把后期单芯片主板、Super Famicom Jr. 或 Mini 外壳混入。

- [Nintendo 日版原始使用说明书镜像](https://manuals.plus/m/935db8250c899ca2991f064b1ab2e027455226b3f20d56ab841e0059be6e954a)：200 × 242 × 74 mm，双 SHVC-005；HVC-002 电源与 SHVC-008 立体声 AV 线另售。在线转写仅用于规格，内部结构不依赖自动转写中的解释。
- [Nintendo 1992 日文维修手册原扫描](https://documents.cdn.ifixit.com/UsnpFRnT5n2fTQrV.pdf)：已核对扫描全册以及印刷页 11–15。原厂爆炸图说明上下壳、顶面板、卡槽盖/弹簧、退卡杆、锁杆、屏蔽、供电开关双线束、前板排线及磁环；零件表明确 62P 卡槽上下连接器。
- [iFixit Super Famicom 实机拆解](https://www.ifixit.com/Teardown/Super+Famicom+Teardown/96507)：已查看 14 张原照片；独立声音模块、两种上屏蔽、底部屏蔽、前端口板与退卡机构。
- [Inviere 原机维修与照片](https://www.boards.ie/discussion/2058337820/super-famicom-a-capacitance-for-greatness)：SHVC-CPU-01 主板、原版外观及打开的 SHVC-SOUND，S-SMP / S-DSP、双音频 RAM、DAC 与放大器分件依据。建模不复制修补痕迹。
- [SHVC-005 控制器实机拆解](https://shattered-blog.com/archives/40877)：已查看六张原照片；双移位寄存器、肩键板触片、独立橡胶触点、五颗后盖螺钉和七触点插头，照片 PCB 标注 1992。
- [ConsoleArtisan 的原版 SHVC-CPU-01 实拍](https://consoleartisan.com/reference/snes/)：S-CPU、S-PPU1 / S-PPU2、S-WRAM、双 VRAM 与 S-ENC 布局补充。该页另有后期单芯片与换壳照片，本模型只采用原版 SHVC-CPU-01 板图。

官方外形包络与局部近似分开记录。壁厚、曲率、螺柱、触点、器件尺寸、弹簧及线缆长度仅作结构学习；不声称原厂 BOM、电路复原或可制造公差。配套两只手柄；若加入 AC 与 AV 线，将明确标为另售的配套学习附件。不添加游戏数据或虚构随箱游戏卡带。

- [HVC-002 原版拆机照片](https://desktopmusik.com/junk/game/family-computer-adapter)：已查看原版外观、插片面、打开外壳与铁芯/滤波板照片。只参考原适配器，没有混入文中另一只现代电源。尺寸近似，非功能模型。
- [SHVC-008 收藏实物照片](https://chromagi.com/nintendo/n64/shvc-008/)：已查看灰色 MULTI OUT 与黄/白/红 RCA 插头。日本标准主机的 AC/AV 另售关系以原版主机手册为准。
- [原版后部接口照片](https://www.nintendolife.com/news/2020/11/hardware_classics_super_famicom)：已查看 MULTI OUT、RF、CH1/CH2、DC IN 排列及后面板通风。
