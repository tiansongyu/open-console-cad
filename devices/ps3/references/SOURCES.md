# PlayStation 3 首发 60GB 家族参考

选择日本 CECHA00 黑色厚机外观，内部参考同代 CECHA01 60GB 拆解。两个地区版本的局部装配差异不据此判定为相同。资料于 2026-10-01 核对，模型已开始分轮构建；本目录尚不表示完成交付。

- [Sony 原版使用说明](https://www.playstation.com/content/dam/global_pdc/en/corporate/support/manuals/ps3-docs/JA_PS3-00-1.0_1_WEB.pdf)，第 20–21 页：60GB、四个 USB、三类读卡接口和公开包络；约 325 × 98 × 274 mm（宽、高、深），不含最大突出部。控制器标示 3.7V、610mAh。
- [Sony 原版快速参考](https://www.playstation.com/content/dam/global_pdc/en/corporate/support/manuals/ps3-docs/JA_PS3-00-1.0_2_WEB.pdf)，第 2、4 页：原配无线控制器、AC / AV / USB / LAN 线；前部读卡盖、四个 USB、吸入盘口和触控键，后部主电源开关、AC、HDMI、LAN、光纤和 AV MULTI。第 11 页的接地说明明确独立接地尾线，模型采用日式两片插头及接地尾线，不混用美式第三插脚。
- [iFixit 首发 60GB 实机拆解](https://www.ifixit.com/Teardown/PlayStation+3+Teardown/1260)，37 步照片：滑动亮面上盖、内罩、独立读卡器和无线板、可抽取 HDD、金属罩电源、光驱、上下屏蔽、底面大风扇、双芯片散热接触与主板。照片上的机器标签为 CECHA01；资料是作者实机观察，不是原厂尺寸图。

建模坐标计划为横置 X 宽 325、Y 深 274、Z 高 98 mm。读卡盖、镀铬前缘和首发无线控制器必须保留；SIXAXIS 采用下述早期独立运动传感器板布局参考，确切主板版本未断言。局部曲线、壁厚、器件、连接和机构尺寸都将单独标为学习近似，不承诺生产公差、功能电路或动态性能。

第三方拆解照片与原版手册只在本地参考目录保存，不作为本仓库作品重新分发。

- [Dark Pallacus 的实机拆装对照](https://daxhordes.org/forum/viewtopic.php?t=5)，2009-09-03：作者分别展示 SIXAXIS 和 DualShock 3。已检查全部图片，建模只采用 SIXAXIS 的无振动电机、独立运动传感器板及三线连接、复位延长件、按键薄膜和 Mini-B 接口；不把 DualShock 3 的马达与板件套入首发控制器。

主板采用 COK-001 同代可见器件分布，保留 Cell / RSX 朝向散热侧和独立 EE+GS。四 USB 通过端子与主板连接，单独无线模块及小型天线板参考拆解第 15–17 步。硬盘内部沿用通用 2.5 英寸单盘片结构示意，不断言首发 60GB 实机供应商、盘片数量或精确内部尺寸。

- [Sony CECHA00/A01 60GB 维修手册第三版](https://documents.cdn.ifixit.com/6wdEAkIyJYsjXkBP.pdf)，2007-05，编号 SM-PS3-0013E-02，iFixit 托管。已核对第 31–36 页爆炸图：上下盖、读卡板、无线板、触控板、电源、光驱、下方风扇与双处理器热交换器、HDD、屏蔽板及无振动 SIXAXIS 的层次；第 34 页列有风扇与 HDD 型号，不能据此声称所有批次都相同。模型采用十九叶风扇结构示意，局部尺寸及管路不作原厂精确复刻。
