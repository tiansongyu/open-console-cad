# Sony PlayStation 3 · CECHA00

首发日本 60GB 结构学习模型正在构建，尚未加入网页目录。外观依据 CECHA00 官方手册，内部依据 Sony CECHA00/A01 维修手册及同代 CECHA01 实机拆解；局部曲率、板件布局和机构尺寸为学习近似。

当前源码实现 14 轮：可编辑弧形外壳、四 USB 与原版后部接口、三格式读卡器、侧抽 HDD、COK-001 同代主板、无线与触控板、下方大风扇/双处理器散热、金属罩电源、吸入式光驱及上下主板屏蔽。前 14 轮共 1,162 个组件，全部严格 BRep、2,192 对装配候选和从空文档重建后的逐组件几何比对通过。该里程碑仍不是最终交付。

控制器将采用早期无振动电机的 SIXAXIS；附件按原版 AC / AV / USB / LAN 套装。线束、控制器、附件、最终导出、图册和网页仍在后续任务中。

参考 [版本资料](references/SOURCES.md)、[阶段记录](ITERATIONS.md)。源码位于 [ps3.py](../../tools/cadlib/ps3.py)，[重建宏](Rebuild_PlayStation3.FCMacro) 执行全部已实现阶段，并写入本地 `output/rebuilt` 目录。
