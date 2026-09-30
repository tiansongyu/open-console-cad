# 按销量扩充十个平台

用户于 2026-09-30 要求：完成当前未完成任务后，继续后续交付，再根据销量新增十个游戏主机，直到全部完成。

## 顺序与完成标准

1. 完成当前 PS2（SCPH-10000）控制器、记忆卡及配套附件。
2. 完成 PS2 全部原生重建、严格 BRep、装配干涉、STEP 往返、组件清单、十二页 A3 图册及网页交付检查，使原有十七个平台全部交付。
3. 根据有日期和来源的累计硬件销量选择十个尚未收录的平台，逐个完成相同交付标准。
4. 对最终二十七个平台统一核对目录、文件哈希、组件数量、下载链接和网页行为。

不得把原有十七个平台交付误记为本任务完成。新增平台需要各自的来源资料、可重建源码和独立检查记录；外形公开规格与局部近似尺寸需明确区分。

## 销量口径

用户已确认：全球累计硬件销量，包含掌机；地区名称及改款合并为同一平台，排除已有平台。

优先使用厂家财报、投资者关系资料和官方历史统计。停产平台缺少官方最终累计数据时，明确区分最后公布值与第三方估算；在售平台记录统计截止日期。不要把收入、出货增量、活跃用户或软件销量当作累计硬件销量。以下为截至 2026-10-01 查证的扩充顺序；各来源的统计时间和口径并不完全相同，因此不是同一时点的精确销售排行榜。

## 当前进度

- 原有目录包含十七个平台；PS2 的原生工程、三份 STEP、12 页图册与 21 个网页视图已完成验证，公开部署 `5390d3b` 的 14 个文件、21 个视图和三种屏幕布局也已核对通过。
- 接手时 PS2 正式记录到第 24 轮，工作区已有第 25–29 轮控制器模型，存在未解决的装配干涉。
- PS2 套装已推进到第 34 轮：1,352 个组件、6,992 个实体，已补齐控制器、记忆卡、连接线及空白介质；整套重建、严格实体、装配求交、STEP 回读、图册独立审阅和网页布局检查通过。
- 新增十个平台的资料核对已完成；PS4 已完成 29 轮建模、1,039 个组件和 1,133 个实体；重建、严格几何、2,225 对装配候选、三份 STEP、参数修改复原、12 页图册及独立审阅通过，20 个网页视图和三种屏幕布局通过，公开部署待核对。用户进一步确认包含 Game & Watch 固定游戏掌机系列，GameCube 顺延。


## 新增十个平台与销量证据

单位：百万台。`>` 保留官方“超过”口径；估算不表示厂商认证。改款合并用于销量筛选，每个平台选择一款代表硬件建模，不把所有改款做成重复条目。

| 顺序 | 平台 | 全球累计 | 数据日期 / 性质 | 代表版本与进度 |
| --- | --- | --- | --- | --- |
| 1 | PlayStation 4 | >117 | 2022-06-30，Sony 官方 sell-in | CUH-1000A 黑色原版；完整本地交付通过，公开部署待核对 |
| 2 | PlayStation 5 | >95 | 2026-06-30，Sony 官方 sell-in | CFI-1000A 原版光驱机；外壳、接口及底座 4 轮、145 组件，内部结构待继续 |
| 3 | PlayStation 3 | >87.4 | 2017-03-31，Sony 官方 sell-in | 原版厚机；待建模 |
| 4 | Xbox 360 | >84 | 2014-06-09，Microsoft 官方供货至零售 | 原版白色；待建模 |
| 5 | Game Boy Advance | 81.51 | Nintendo 历史累计，2026-06-30 统计表 | AGB-001；待建模 |
| 6 | Xbox One | 57.96 | VGChartz 平台累计估算，2026-10-01 查询 | 原版黑色；待建模 |
| 7 | Super Nintendo / Super Famicom | 49.10 | Nintendo 历史累计，2026-06-30 统计表 | SHVC-001；待建模 |
| 8 | Game & Watch | 43.40 | Nintendo 官方历史系列累计 | 双屏 Donkey Kong DK-52 代表系列；待建模 |
| 9 | Xbox Series X / S | 35.21 | VGChartz 截至 2026-08-01 的零售估算 | Series X CFI-1000A 原版光驱机；外壳、接口及底座 4 轮、145 组件，内部结构待继续 |
| 10 | Xbox | >24 | 2006-05-09，Microsoft 官方累计 | 原版黑色；待建模 |

数据来源：

- [Sony Business Data & Sales](https://sonyinteractive.com/en/our-company/business-data-sales/)：PS4、PS5、PS3 官方硬件累计，sell-in 定义包含退回再销售的翻新硬件；使用页面公布的舍入数字。
- [Nintendo 历史硬件销售](https://www.nintendo.co.jp/ir/en/finance/hard_soft/index.html)：GBA、SNES 和候补 GameCube。GBA SP / Micro 合并，地区名称合并。
- [Nintendo Iwata Asks：Game & Watch](https://www.nintendo.com/en-gb/Iwata-Asks/Iwata-Asks-Game-Watch/Iwata-Asks-Game-Watch/4-Absorbed-in-Development/4-Absorbed-in-Development-223140.html)：日本 12.87 百万台、海外 30.53 百万台。43.40 百万是原历史系列合计，不是 DK-52 单机销量，也不把现代纪念版计入这个数字。
- [Xbox Wire，2014-06-09](https://news.xbox.com/en-us/2014/06/09/events-e3-2014-recap/)：Xbox 360 已超过 84 百万台供货零售；这是最后阶段的官方公布值，不冒充最终精确累计。
- [Microsoft，2006-05-09](https://news.microsoft.com/source/2006/05/09/gamers-catch-their-breath-as-xbox-360-and-xbox-live-reinvent-next-generation-gaming/)：原版 Xbox 全球超过 24 百万台。
- [VGChartz 平台硬件累计表](https://www.vgchartz.com/charts/platform_totals/Hardware.php/)：Xbox One 57.96 百万，第三方估算；Microsoft 未在该表提供独立最终确认。
- [VGChartz，2026 年 7 月估算，发表于 2026-08-11](https://www.vgchartz.com/article/468786/ps5-outsells-switch-2-worldwide-hardware-estimates-for-july-2026/)：Xbox Series 累计 35,206,081 台，明确为零售估算。

去重：Game Boy / Color 作为已有 Game Boy 家族处理；DS、3DS、PSP、Vita、Switch 等已收录家族不重复。用户于 2026-10-01 明确选择包含固定游戏掌机，因此 Game & Watch 列入本批，GameCube（Nintendo 官方 21.74 百万台）排在本批之后。
