# Open Console CAD

**用 FreeCAD 构建、可以在浏览器中拆开观察的游戏主机模型。**

[在线 3D 模型库](https://tiansongyu.github.io/open-console-cad/) · [下载整个仓库](https://github.com/tiansongyu/open-console-cad/archive/refs/heads/main.zip) · [MIT 协议](LICENSE) · [第三方声明](THIRD_PARTY_NOTICES.md)

目前已完成 Nintendo Switch、Nintendo Switch 2 和 Nintendo 3DS 三个独立设备项目：原生可编辑模型、建模源码、爆炸装配、STEP、A3 工程图和实际 CAD 效果图。网页使用 Three.js 显示从 FreeCAD 实体导出的 GLB，**无需安装 FreeCAD 即可旋转、缩放和探索装配结构**。

## 点击设备，直接预览

| Nintendo Switch · HAC-001 | Nintendo Switch 2 · BEE-001 |
| --- | --- |
| [![Nintendo Switch 3D 预览](site/public/images/switch/hero.webp)](https://tiansongyu.github.io/open-console-cad/?device=switch&view=assembled#viewer) | [![Nintendo Switch 2 3D 预览](site/public/images/switch2/hero.webp)](https://tiansongyu.github.io/open-console-cad/?device=switch2&view=assembled#viewer) |
| [整机 3D](https://tiansongyu.github.io/open-console-cad/?device=switch&view=assembled#viewer) · [内部结构](https://tiansongyu.github.io/open-console-cad/?device=switch&view=internal#viewer) · [主机爆炸](https://tiansongyu.github.io/open-console-cad/?device=switch&view=exploded#viewer) | [整机 3D](https://tiansongyu.github.io/open-console-cad/?device=switch2&view=assembled#viewer) · [内部结构](https://tiansongyu.github.io/open-console-cad/?device=switch2&view=internal#viewer) · [主机爆炸](https://tiansongyu.github.io/open-console-cad/?device=switch2&view=exploded#viewer) |
| [设备说明](devices/switch/README.md) · [A3 图册](devices/switch/output/drawings/Switch_Drawings.pdf) | [设备说明](devices/switch2/README.md) · [A3 图册](devices/switch2/output/drawings/Switch2_Drawings.pdf) |

网页还有手柄、底座和附件视图，底部的效果图库可点击查看大图。

| 项目 | Switch | Switch 2 |
| --- | ---: | ---: |
| 建模迭代 | 14 轮 | 15 轮 |
| 物理组件 | 654 | 799 |
| CAD 实体 | 835 | 963 |
| 图册 | 12 页 A3 | 12 页 A3 |
| 手持包络，含摇杆与扳机 | 239 × 102 × 28.4 mm | 272 × 116 × 30.7 mm |
| 主体厚度 | 13.9 mm | 13.9 mm |
| 网页 GLB | 约 9.9 MB | 约 13.4 MB |

**范围说明：**这些是非官方 CAD 学习模型。整体包络参考公开规格，局部尺寸、壁厚、孔位、安装间隙和内部模块是近似设计。主板、芯片、天线等不包含真实电路或制造资料；Switch 2 以 2025 年首发 BEE-001 为对象。参考依据在各设备的 `references/SOURCES.md`。

## 扩展设备

| 设备 | 状态 / 直接预览 | 模型与图纸 |
| --- | --- | --- |
| Nintendo 3DS CTR-001 | [展开](https://tiansongyu.github.io/open-console-cad/?device=3ds&view=assembled#viewer) · [闭合](https://tiansongyu.github.io/open-console-cad/?device=3ds&view=closed#viewer) · [爆炸](https://tiansongyu.github.io/open-console-cad/?device=3ds&view=exploded#viewer) | [设备说明](devices/3ds/README.md) · [A3 图册](devices/3ds/output/drawings/Nintendo3DS_Drawings.pdf) |
| Nintendo DS NTR-001 | 制作中 | [参考与配置](devices/nds/profile.json) |
| PSP-1000 | 制作中 | [参考与配置](devices/psp/profile.json) |
| PS Vita PCH-1000 OLED | 制作中 | [参考与配置](devices/psv/profile.json) |
| Steam Deck LCD（2022） | 制作中 | [参考与配置](devices/steamdeck/profile.json) |

[![Nintendo 3DS 可开合模型](site/public/images/3ds/hero.webp)](https://tiansongyu.github.io/open-console-cad/?device=3ds&view=assembled#viewer)

目标是七款设备。只有完成几何、图纸和预览核验的设备才加入线上目录，阶段进展见 [扩展计划](docs/SEVEN_DEVICE_PLAN.md)。

## 怎么使用网页

1. 点击设备卡片切换 Switch / Switch 2。
2. 选择整机、内部结构、主机爆炸、手柄、底座或附件。
3. 鼠标拖动旋转、滚轮缩放、右键拖动平移；手机支持单指旋转、双指缩放和平移。
4. 用“展开程度”滑块从装配状态过渡到分层状态。“主机爆炸”默认完全展开。
5. 使用重置视角、自动旋转或全屏按钮。3DS 等折叠设备另有开合角度滑块。画布获得焦点后可用方向键旋转、`+` / `-` 缩放。
6. 页面提供 FreeCAD、PDF 和 GLB 下载链接。效果图始终可查看，WebGL 不可用或模型加载失败时有明确提示和重试入口。

链接中的 `device` 和 `view` 参数可以分享，例如：

```text
https://tiansongyu.github.io/open-console-cad/?device=switch2&view=exploded#viewer
```

## 仓库目录

```text
open-console-cad/
├── devices/
│   ├── switch/
│   │   ├── README.md / ITERATIONS.md
│   │   ├── Open_Switch.FCMacro / Rebuild_Switch.FCMacro
│   │   ├── scripts/       # 按轮次组织的 FreeCAD Python 源码
│   │   ├── references/    # 来源说明、标识轮廓、CAD 字体及其许可
│   │   └── output/        # FCStd、STEP、组件清单
│   │       ├── drawings/  # PDF、SVG、内容数据和图纸模板
│   │       ├── previews/  # 原生 CAD 渲染
│   │       └── reports/   # 几何、重建、尺寸与导出检查
│   └── switch2/           # 同样的独立结构
├── site/
│   ├── index.html
│   ├── src/               # Three.js 交互逻辑与响应式样式
│   └── public/
│       ├── models/        # GLB 与可核对的导出清单
│       └── images/        # 网页效果图
├── tools/                 # FreeCAD → GLB、仓库与 glTF 检查
├── docs/                  # 建模集成与维护说明
├── licenses/              # 第三方许可证副本
├── .github/workflows/pages.yml
├── LICENSE
└── THIRD_PARTY_NOTICES.md
```

不提交运行日志、个人机器路径、备份、虚拟环境、下载的研究照片或网页副本。历史各轮的二进制快照可通过源码重新生成；Git 中保留最终模型和全部建模阶段源码，避免持续累积大型二进制历史。

## 在 FreeCAD 中打开和修改

```bash
git clone git@github.com:tiansongyu/open-console-cad.git
cd open-console-cad
```

推荐使用 **FreeCAD 1.1.3**，这是原模型验证使用的版本。

- 在 FreeCAD 中打开设备目录下的 `Open_Switch.FCMacro` 或 `Open_Switch2.FCMacro`，通过“宏 → 宏 → 执行”运行，打开完整模型、爆炸装配和图纸。
- 也可直接打开 `output/*_Complete.FCStd`。默认显示手持整机，底座和附件位于独立分组。
- `*_Exploded.FCStd` 记录组件编号和爆炸位移，可观察各装配层。
- `*_Drawings.FCStd` 为当前版本的自包含矢量图页和可测尺寸参考。**修改三维模型后需要重新生成图纸**，它不是自动跟随所有几何变化的完整关联工程图。
- 使用参数表 `Parameters` 调整参数；已验证 `StickProjection` 的摇杆联动。其他参数受上下游几何依赖影响，改后应重新计算并检查。
- 运行 `Rebuild_*.FCMacro` 会按顺序执行该设备的 `iter01_*.py` 至最后一轮，在设备的 `output/rebuilt/` 中生成结果，保留交付文件。

| 格式 | 用途 |
| --- | --- |
| `.FCStd` | FreeCAD 原生几何、建模历史和参数，是继续设计的入口 |
| `.step` | 通用 CAD 交换，保留实体与颜色，不保留 FreeCAD 建模历史 |
| `.glb` | 浏览器展示网格，保留组件与颜色，不是精确 CAD 实体 |
| `.pdf` / `.svg` | 可阅读、打印或编辑的图纸 |
| `COMPONENTS.csv` | 零件编号、分组、材质显示角色与尺寸索引 |

## 在本地运行网页

需要 Node.js 24 和 npm；查看网页本身不需要 FreeCAD。

```bash
npm ci
npm run dev
```

打开终端显示的本地 URL。生产构建：

```bash
npm run check
npm run build
npm run preview
```

`npm run check` 检查 GLB 与 CAD 文件的 SHA-256、组件编号一致性、FCStd 压缩包完整性、必要文件、Python 语法及 Khronos glTF 验证器结果。GLB 已提交，因此 GitHub Actions **不需要安装或启动 FreeCAD**。

## 从 FreeCAD 更新网页模型

先保存设备的最终 FCStd，并同步其 `output/reports/final_manifest.json`，然后在 FreeCAD 的 Python 控制台运行：

```python
repo = "/absolute/path/open-console-cad"
exec(open(repo + "/tools/export_web_models.py", encoding="utf-8").read())
export_device(repo, "switch")
export_device(repo, "switch2")
```

也可通过 [freecad-mcp](https://github.com/neka-nat/freecad-mcp) 的 `execute_code` 执行以上代码，见 [MCP 说明](docs/MCP.md)。

导出器逐组件读取真实 BRep，用 MeshPart 生成网格，将 mm 转为 glTF 的 m。默认线性偏差设为 0.25 mm、角度偏差为 0.45 rad，保留颜色、组件编号、装配分组及爆炸位移。网页 GLB 的身份和源文件哈希记录在 `site/public/models/*.json`。**导出不会改写 FCStd 或 STEP。**

如果改了几何，还应重新导出 STEP、生成尺寸图并执行设备脚本中的相关 CAD 检查。图纸的 PDF 生成沿用 Kami：安装 Kami 后设置 `KAMI_HOME`，运行设备下的 `build_drawing_book.py`，并执行其字体、内容和逐页视觉检查；单纯更新网页不需要重新生成 PDF。

## GitHub Pages 发布

在线地址：**https://tiansongyu.github.io/open-console-cad/**

仓库的 `.github/workflows/pages.yml` 在推送 `main` 后自动检查、构建并发布 `dist/`。依赖锁定于 `package-lock.json`，Actions 固定到提交 SHA。构建使用相对资源路径，可部署在 `/open-console-cad/` 项目子目录下。

首次在新仓库启用时：仓库 **Settings → Pages → Build and deployment → Source → GitHub Actions**。Fork 后需要在自己的仓库启用 Pages，并修改 README 和 `site/src/main.js` 中指向原仓库的链接。

更多维护与新增设备步骤见 [维护指南](docs/MAINTAINING.md)。

## 模型检查记录

原始最终 CAD 已通过实体有效性、干涉、参数修改恢复、源码重建、STEP 回读和尺寸核对。具体证据位于各设备 `output/reports/`，检查针对记录的模型版本；这些历史报告不意味着所有后续修改自动通过。

- Switch：最终检查 1,029 对候选组件，14 轮源码构建匹配；26 项模型尺寸、23 项原生图纸尺寸参考。
- Switch 2：最终检查 1,375 对候选组件，15 轮源码构建匹配；26 项模型尺寸、22 项原生图纸尺寸参考。
- 两份 PDF 均为 12 页 A3，已完成 Kami 构建、中文字体、内容覆盖和逐页视觉检查。

## 贡献与协议

欢迎通过 Issue 或 Pull Request 改进建模结构、补充设备和提升网页体验。请附参考来源、修改前后预览及相关验证结果，见 [CONTRIBUTING.md](CONTRIBUTING.md)。

项目原创内容采用 **[MIT License](LICENSE)**。Nintendo 名称、标识、参考材料及第三方依赖保留其原有权利，具体范围见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。本项目与 Nintendo 无隶属关系。
