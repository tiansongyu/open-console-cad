# Xbox One 原版资料与建模边界

核对日期：2026-10-09。选择 2013 年原版黑色 500 GB / Model 1540；普通黑色 1537 手柄及 Kinect 2。交付内容与验证状态见项目 README 和 output/reports/。

- [Microsoft 官方家族规格表](https://news.xbox.com/wp-content/uploads/sites/2/Xbox_One_Spec_Sheet.pdf)：原版 Xbox One 一列给出 34.3 × 26.3 × 8 cm，本模型采用 343 × 263 × 80 mm 的发布包络；不把其他改款的尺寸或未经核对的常见二手数值替代此依据。外置电源、8 GB DDR3、Blu-ray、HDMI 输入/输出与专用 Kinect 接口按原版区分。
- [iFixit 原版 Xbox One 拆解，2013-11-21](https://www.ifixit.com/Teardown/Xbox+One+Teardown/19718)：实物型号 1540，原生外壳、金属屏蔽、112 mm 风扇、三路铜热管、光驱、2.5 英寸硬盘及主板布局参考。已逐图核对 43 张照片。拆解中的 Day One 手柄字样不复制到普通版。
- [Microsoft 提交 FCC 的原版 1537 内部照片](https://fccid.io/C3K1537/Internal-Photos/Internal-Photos-2022366.pdf)：2013 年申请，2013-11-22 公开，六页原始照片均已核对。双电路板、射频子板、双 AA 接触片、两个摇杆、十字键金属圆片、ABXY 胶膜及四组振动机构分别建立。原版仅保留 micro-USB 与专用耳机接口，不加入后期 3.5 mm 孔、蓝牙或 USB-C。
- [iFixit Xbox One Kinect 拆解，2013-11-22](https://www.ifixit.com/Teardown/Xbox+One+Kinect+Teardown/19725)：已核对 34 张照片，区分手动俯仰底座、背面小风扇、双板、RGB 与红外镜头、三窗红外发射组件、金属散热条和麦克风。

局部尺寸、壁厚、开孔、螺钉、弹簧、封装、线路及线缆路径为非功能性结构学习近似，不提供制造公差或电气设计。参考照片只用于观察，不随模型重新发布。配套外置电源依据早期实机拆解，保留离心风扇、独立屏蔽与元件包络；地区 AC 及 HDMI 线缆为缩短的陈列版本，局部尺寸近似。

排除混用：iFixit 72986 虽归在 1537 设备目录，其内部照片出现后期 3.5 mm 插座，不能作为原版主板的主要依据；本模型采用 FCC 原始图。


- [首发原装外置电源拆解](https://www.ifixit.com/Guide/Xbox+One+Power+Brick+(Day+One+Edition)+Disassembly/66171)：作者首发日购入设备的实拍，已检查全部 17 张照片；依据外壳、四脚垫、离心风机、导风框、金属屏蔽、主板与 LED 导光建立结构近似。
- [Kinect One 线缆接点实测记录](https://sureshsubedi.wordpress.com/2022/04/24/kinect-one-cable-pinout/)：专用口 5+8 接点分区的第一手记录。模型仅显示结构分区，不表示电气定义或接线指导。

- [Microsoft News Center，2013-08-09 首发开箱说明](https://news.microsoft.com/es-es/2013/08/09/no-te-pierdas-el-impresionante-unboxing-en-video-de-xbox-one/)：确认首发 Kinect、双 AA / micro-USB 手柄、四麦克风、聊天耳麦及 HDMI/电源线。文章展示 Day One 特别版；本工程以普通黑色 Model 1540 为主体，配套机构参照同代首发说明，不复制特别版手柄的镀铬十字键与 DAY ONE 字样。耳麦与外置电源局部几何近似，区域 AC 插头采用明确的两脚展示变体。
