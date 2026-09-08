# Switch 2 尺寸与外观依据

核对日期：2026-09-08。对象为 2025 年首发 BEE-001；后续地区维修结构变更不在此模型范围内。

| 依据 | 用途 |
|---|---|
| [Nintendo 日本官网规格](https://www.nintendo.com/jp/hardware/switch2/specs/index.html) | 手持整机 272 × 116 × 13.9 mm，最大厚度 30.7 mm；Joy-Con 2 含连接突起 41.4 × 116 × 30.7 mm；底座 201 × 115 × 51.2 mm；握把 144 × 116 × 40.8 mm；腕带框架 16.4 × 116 × 7 mm |
| [Nintendo 各部位名称](https://support.nintendo.com/jp/switch2/prepare/partsname/index.html) | 双 USB-C、U 形支架、磁吸释放键、鼠标窗、C 键、LED、底座 LAN 和附件布局 |
| [iFixit 2025 年首发现场拆解](https://www.ifixit.com/News/110926/switch-2-teardown) | 5220 mAh 电池、500 mAh 手柄电池、主板/双 UFS、风扇/热管、鼠标小板、底座主动散热和弹簧浮动插头等主要模块的布局参考 |
| [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp) | 全部 Switch 2 绘制、装配修正与 FreeCAD 图纸创建通过此 MCP 执行；使用版本 0.1.22，提交 3da6db5f71a7b74d1b69d295d1ba89233ad622b5 |

主机单体 198 mm 宽度是本模型比例近似。7.9 英寸显示区采用 16:9 比例推算为约 174.89 × 98.38 mm。局部尺寸、内部厚度、磁体位置、电路布局和紧固件均为观察用途近似设计，不是制造工程资料。英国页面的手柄宽度与日文规格不一致，本项目采用日文官方规格，未将矛盾数值混用。

`switch_mark.svg` 来自官方产品图的矢量标识。SVG 填充轮廓使用本项目 `svg_exact.py` 转换，避免普通导入遗漏字符。DejaVu 字体许可证随项目提供；中文 PDF 字体由本机 Kami 流程嵌入，未打包商业字体文件。
