# 维护与新增设备

## 数据来源

网页的每个 GLB 节点对应一个原生物理组件：`partId`、`partNumber`、`assembly`、`material` 和 `explodeOffset` 记录在节点 `extras` 中。Three.js 的 GLTFLoader 读取后，查看器按装配分组显隐，并将爆炸位移乘以滑块比例。

这是模型的展示变换，不会修改下载的原生装配。网页没有后台、登录、分析追踪或在线模型转换服务。

## 更新已有设备

1. 在设备目录修改 FreeCAD 源码和模型。
2. 使用该设备脚本重新生成最终 FCStd、STEP、组件清单与 `final_manifest.json`。
3. 重新执行相应的几何、干涉、参数与 STEP 检查。明确记录检查对象版本。
4. 更新图纸时使用 `drawing_geometry.py` 和 Kami 的 `build_drawing_book.py`，按 Kami 流程检查字体、内容、布局及每页渲染。
5. 通过 FreeCAD / MCP 运行 `tools/export_web_models.py`，更新 GLB 和哈希清单。
6. 更新 `site/public/images/<device>/` 中的自制效果图及设备说明。
7. 执行 `npm ci && npm run check && npm run build`；在浏览器测试整机、内部、爆炸、底座、设备切换和手机布局。
8. 提交到 `main`，等待 Pages 工作流成功后验证线上地址。

网页不会自动读取改过的 FCStd；只有重新导出并提交 GLB 后才会更新。原生模型与网页模型的源文件 SHA-256 必须一致，CI 会检查这一点。

## 新增设备

- 按 `devices/<device>/` 组织独立源码、宏、来源资料和输出。
- 给每个物理组件分配稳定标识，提供与现有格式一致的 `final_manifest.json`。
- 在 `site/src/catalog.json` 中登记经过验证的设备、视图分组和效果图。目录同时驱动网页和 CI 检查，不再维护多个硬编码列表。
- 添加 GLB、导出清单和网页效果图，扩展仓库检查并更新 README 的数量和预览链接。
- 自制效果图可以提交；第三方图片需先确认授权并保留归属。不要把下载的研究资料直接纳入 MIT。

## 发布与资源大小

- GitHub Pages 只发布构建后的 `dist/`；FCStd、STEP 与 PDF 通过仓库链接下载。
- 网页 GLB 提交在 Git 中，不使用 Git LFS，避免 Pages 读取到 LFS 指针。
- 当前每个网页模型约 10–14 MB。新增设备时先调整网格偏差，再检查视觉质量；不要直接发布 CAD 默认显示缓存生成的过密网格。
- 原始毫米几何在网页导出时转换为米；不要再次在 JavaScript 中缩放 1/1000。
- 二进制历史阶段、构建缓存和虚拟环境不提交。将最终文件与源码保存即可。

## 许可文件

根目录 MIT 不覆盖第三方商标、素材和依赖。新增依赖或模板时同步更新 `THIRD_PARTY_NOTICES.md` 和 `licenses/`。保留字体和上游模板的原有许可。
