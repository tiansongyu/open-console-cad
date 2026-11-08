# Nintendo Famicom HVC-001 — sources

- [Nintendo original hardware and manual specifications](https://www.nintendo.com/jp/famicom/hardware/index.html): HVC-001 body width 150 mm, depth 220 mm, height 60 mm; DC 10 V / 850 mA adapter, approximately 4 W; RF, AC, channel/mode switches and front expansion connector. First controller has START/SELECT; second has microphone and volume. Official product photographs used to establish body axes. Reviewed 2026-09-09.
- [iFixit firsthand teardown, guide 3199](https://www.ifixit.com/Teardown/Nintendo+Family+Computer+(Famicom)+Teardown/3199): red/cream HVC-001, round-button controllers, six bottom screws, eject linkage, motherboard and power/RF sections. The photographed HVC-CPU-GPM-02 board is a reference revision, not a claim to reproduce the earliest 1983 electronics.

The model uses the familiar round-button original housing rather than the initial square-button controller revision, AV Famicom, NES or Mini. The published body envelope sets the CAD axes (X across the front; Y front to rear; Z vertical). Wall thickness, sloping faces, fasteners, connectors and electronic packages are approximate study dimensions. Research photographs remain local and are not redistributed. DejaVu Sans retains the root font license.

Additional official photographs reviewed: controller II has a raised 23-hole microphone field and a volume slider above the D-pad; the HVC-002 adapter, cream HVC-003 RF switch with antenna screw clamps, and twin-lead HVC-004 converter set the accessory exterior references. Accessory dimensions, winding volumes and electronic packages are explicitly approximate.

## 第 17 轮接口与外观校准

详细 URL、适用范围和参考文件哈希见 [fidelity_iteration17.json](fidelity_iteration17.json)。Nintendo 的 HVC-001 官方照片用于核对扩展口侧别、13 条后部散热槽、控制凹面与铭牌。TinyNES 开发者和可追溯 GPM-02 PCB 封装提供 2.54 mm 卡带节距与 5.08 mm PCB 引脚排距；不能据此推导原装弹片形状。Amphenol 名义 DA-15 格距、Same Sky RCA 图纸和兼容电源板的 5.5 × 2.1 mm DC 接口仅约束配合接口，不代表已确定任天堂 OEM 料号。

机壳细曲面、内部布置、线缆长度、字形、颜色及未给出公差的局部尺寸仍为重建近似值。当前严格几何与装配检查不等于制造互换性或电气功能验证。
