# 使用 freecad-mcp

项目建模使用 [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp)。原始集成记录使用版本 0.1.22，提交 `3da6db5f71a7b74d1b69d295d1ba89233ad622b5`。请以该项目的安装文档为准。

1. 安装 FreeCAD。将上游 `addon/FreeCADMCP` 放入当前 FreeCAD 的用户 Mod 目录。
2. 重新启动 FreeCAD，选择 MCP Addon 工作台，启动 RPC Server。默认仅绑定 `127.0.0.1:9875`。
3. 在支持 MCP 的客户端配置服务，例如：

```json
{
  "mcpServers": {
    "freecad": {
      "command": "uvx",
      "args": ["freecad-mcp==0.1.22", "--host", "127.0.0.1"]
    }
  }
}
```

先调用 `get_rpc_status` 和 `list_documents`，确认连接成功，再使用 `execute_code` 执行建模或导出。较长的重建应按 `iterNN_*.py` 分轮调用，避免超过客户端或 GUI 调度的超时。

## 网页导出示例

将以下 Python 代码作为 `execute_code` 的 `code`，把 `include_screenshot` 设为 `false`：

```python
repo = "/absolute/path/open-console-cad"
exec(open(repo + "/tools/export_web_models.py", encoding="utf-8").read())
export_device(repo, "switch2")
```

导出读取实际 FCStd 组件，写入 `site/public/models/switch2.glb` 及清单。提交这两个文件后，Pages 可直接更新，无需在线启动 FreeCAD。

## 常见问题

- **连接失败**：确认 FreeCAD 已运行、Addon 已加载、RPC Server 已启动，且主机和端口一致。
- **GUI 调度超时**：先检查 FreeCAD 是否还在计算，或是否停在草图编辑、变换任务、弹窗等状态。不要在不清楚前一次操作是否完成时重放修改代码。
- **长任务超时**：按建模阶段拆分操作；先确认保存文件与实体状态，再继续下一阶段。
- **图纸页无法执行三维视角命令**：先使用 `Gui.activateView("Gui::View3DInventor", True)`。项目的打开宏已处理这一点。

服务保持在本机即可。仓库不包含认证信息、个人客户端配置、上游虚拟环境或会话日志。

- **建模线程**：创建/修改文档对象、重计算、保存和视图渲染使用 `execute_code`。`execute_code_async` 仅用于不接触文档和 GUI 的后台计算。
