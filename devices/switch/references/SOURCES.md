# 模型资料与尺寸依据

查阅日期：2026-09-08。参考机型为标准 Nintendo Switch HAC-001 外观与主要内部布局，红蓝 Joy-Con。没有套用 OLED 或 Lite 的轮廓。

| 来源 | 用途 |
|---|---|
| [Nintendo 官方产品页](https://www.nintendo.com/en-gb/Hardware/Nintendo-Switch-Family/Nintendo-Switch/Nintendo-Switch-1148779.html) | 手持整机 239 × 102 × 13.9 mm，含摇杆和扳机最大厚 28.4 mm，6.2 英寸显示屏 |
| [Nintendo 官方数字手册](https://www.nintendo.com/fr-fr/games/oms/Nintendo-Switch-Digital-Brochure/files/assets/common/downloads/publication.pdf) | 单机主体 173 × 101 × 13.9 mm |
| [Nintendo Joy-Con 规格](https://www.nintendo.com/my/hardware/switch/modal/specs/joy-con.html) | 单个手柄含导轨 35.9 × 102 × 28.4 mm，525 mAh 电池，以及左右手柄不同的控制件和传感器 |
| [Nintendo 底座规格](https://www.nintendo.com/my/hardware/switch/modal/specs/dock.html) | 底座 173 × 104 × 54 mm，接口配置 |
| [Nintendo 主机部位说明](https://en-americas-support.nintendo.com/app/answers/detail/a_id/22633) | 顶部、底部、后盖与主机滑轨的部位分布 |
| [Nintendo Joy-Con 部位说明](https://en-americas-support.nintendo.com/app/answers/detail/a_id/22634) | 面按键、肩键、滑轨键、释放键、玩家灯与右手柄红外窗口 |
| [Nintendo 底座部位说明](https://en-americas-support.nintendo.com/app/answers/detail/a_id/22635) | 两个侧 USB 口、后部电源/USB/HDMI，以及后盖 |
| [Nintendo 官方对比页](https://www.nintendo.com/my/hardware/switch/compare/index.html) | 官方红蓝套装图片与标识 SVG |
| [iFixit 2017 年现场拆解](https://www.ifixit.com/Teardown/Nintendo+Switch+Teardown/78263) | 主要模块位置：电池、主板、风扇和热管、屏蔽板、控制器 PCB、振动组件、底座和握把 |

整体包络采用公开尺寸。局部孔位、壁厚、紧固件规格、内部模块尺寸和安装间隙属于本 CAD 研究的近似设计，必须与官方公开尺寸区分。内部电池、电路和机电组件用于观察布局，没有电气功能。图纸中的局部尺寸表示本模型尺寸，不表示 Nintendo 生产公差。

正式交付包仅包含本次生成的图纸、模型和必要的标识轮廓/字体素材，不附带完整转载的网页正文或拆解照片。标识归对应品牌所有。

## 2026-10-13 外形精修（15-16 轮）

以 [Nintendo 官方产品部位图](https://www.nintendo.com/sg/hardware/detail/switch/index.html) 的正面、背面和侧面作为局部轮廓依据，并重新核对 [官方整体规格](https://www.nintendo.com/en-gb/Hardware/Nintendo-Switch-Family/Nintendo-Switch/Nintendo-Switch-1148779.html)。沿用初代 HAC-001 红蓝 Joy-Con，不混用 OLED / Switch 2 外形。

- 保持公开包络：手持宽 239 mm、高 102 mm；主机主体厚 13.9 mm；含摇杆与扳机总厚 28.4 mm。
- Joy-Con 外侧平面圆弧从 15.8 mm 调整为 20.5 mm；贴轨侧小圆角 0.65 mm；前壳滚圆 1.8 mm，后壳滚圆 3.1 mm。这些是参考图拟合值。
- 校准双摇杆、方向键、ABXY、HOME 与截图键布局；面键中心至组中心距离约 7.7 mm。重做窄弧肩键、弯月形扳机、圆形释放键与背面螺钉分布。
- 软化主机前后边缘，修正底缘 IR 窗口、前置扬声器和亮度传感器位置。内部沿用结构示意，并重新检查装配。

官方图片只能约束可见形状；未公开曲率、内壁、制造公差和材料变形不能从照片唯一确定。本版是按公开尺寸建模的外观复刻研究，不能声称与原厂 CAD 或实物扫描完全一致。第三方参考照片仅留作本地研究，没有加入发布包。

## 2026-10-13 公开资料校准（17 轮）

新增 [Nintendo D819642 外观专利的原始 PDF](https://patentimages.storage.googleapis.com/57/37/2a/8dd4c3079855b2/USD819642S1.pdf)，以图 3、4 对照前后外缘过渡；通过 [Nintendo 专利标记页](https://www.nintendo.com/us/patents/)确认其与初代 Joy-Con 的关联。专利是外观图，不是带尺寸和公差的生产图纸。

校准方法、参考文件 SHA-256、像素坐标、圆拟合、按钮检测以及独立外包络样件，见[公开资料研究](../studies/public-reference/README.md)。独立样件记录测量与对照，第 17 轮将其外缘曲面并入整机，同时保留 V16 的内腔及孔位；八个面键采用约 7.6 mm 直径。研究不包含第三方参考原图，也不构成实物精度或机械互换性验证。

## 2026-10-29 按键比例与位置校准

本轮参考 HAC-001 配套的 HAC-015/HAC-016 Joy-Con，不采用 Joy-Con 2 外形。使用 Nintendo 官方部位图的[正面](https://www.nintendo.com/sg/hardware/detail/switch/img/08-local-specs/body-switch03-front.jpg)、[背面](https://www.nintendo.com/sg/hardware/detail/switch/img/08-local-specs/body-switch03-back.jpg)及[导轨侧面](https://www.nintendo.com/sg/hardware/detail/switch/img/08-local-specs/body-switch03-side.jpg)，并以 D819642 图 3–8 交叉核对左手柄形状；该专利后续的宽机身实施例不用于本轮尺寸拟合。来源 URL、文件 SHA-256、像素范围和换算方法见[按键校准记录](control_calibration.json)。

前视图以壳顶、壳底和内侧直边为位置基准；导轨侧图分别量取侧键、SYNC 与四颗玩家灯的中心。公开的 102 mm 高度用于模型比例换算，帽体、孔沿、装饰环、字形和阴影分别辨认。以下是本轮采用的建模值，单位为 mm；X、Y、Z 坐标沿用现有整机模型。

| 部位 | 采用值与位置 |
| --- | --- |
| HOME | 灰色芯直径 6.1，外环外径 8.4、内径 6.3；黑色房屋图形；中心 X=96.6、Y=-22 |
| 截图键 | 方形边长 6.3，内部圆图案外径 4.1；中心 X=-96.6、Y=-22 |
| ABXY 字形 | 实际字高 3.05，按字形边界居中 |
| 方向三角 | 宽 2.6、高 2.2，随按键方向旋转，采用深色 |
| SL/SR | 帽体宽 3.6、长 8.2；上键 Y=23.5、下键 Y=-18；左上 SL、左下 SR，右上 SR、右下 SL |
| SYNC | 可按面直径 3.1，Y=-6 |
| 玩家灯 | 四个中心 Y=12、8、4、0；与 SL/SR、SYNC 同处 Z=7.4 的导轨中心线 |

八枚圆形面键保留直径 7.6、中心至组中心距离 7.7；摇杆帽保留直径 15.8。+/-、肩键、后扳机和释放键经图像复核后保留现有尺寸：正面暗轮廓可能包含孔沿和阴影，现有资料不足以支持更小幅度的调整。

上述局部值均为图像估计。选边、缩放和遮挡带来的局部估计误差约为 0.3–0.5 mm；这不是原厂公差，也不是经过实机测量验证的误差上限。改用包含顶部微小突出部位的整高作为缩放基准，还会使部分估计变化约 0.7 mm，记录中单独说明了这一影响。专利图没有制造尺寸，营销图也不是经标定的正投影照片，因此这些资料不能证明原厂一致性或零件互换性。本节只记录参考依据与采用值，不替代 CAD 几何和装配检查。

## 2026-11-08 microSD and reproducibility review

The [SD Association overview](https://www.sdcard.org/developers/sd-standard-overview/) supplies the nominal 11 × 15 × 1 mm microSD form factor and eight legacy contacts. [Nintendo's microSD FAQ](https://www.nintendo.com/en-gb/Support/Nintendo-Switch/microSD-Card-FAQ-1500171.html) confirms the original Switch card family and that cards are sold separately. The existing card remains a generic study object; local keying, pad geometry and reader clearance are fitted. Evidence and limits are in [fidelity_20261108.json](fidelity_20261108.json).

The explicit exterior rotation in iteration 15 restores reproducibility of the accepted shoulder legends and IR insert. Glyph union and unrefined speaker cuts preserve represented material by bidirectional Boolean checks. The segmented helix repair retains its original construction parameters but is not certified equivalent to the defective legacy C0 sweep. Four Joy-Con shell curve-on-surface diagnostics remain unresolved.
