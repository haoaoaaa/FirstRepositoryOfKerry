# 711 便利店 POS 系统

2026 Dian 团队秋招大一题：命令行交互式 POS（收银）系统。
纯 C 实现，无第三方依赖。

## 当前进度

| 关卡 | 内容 | 状态 |
| --- | --- | --- |
| Level 0 | 环境配置 / Git / hello world | 🚧 进行中 |
| Level 1.1 | 计价与输出（条码查询、`prices`） | ⬜ 未开始 |
| Level 1.2 | 订单结账（购物车、`print`/`checkout`） | ⬜ 未开始 |
| Level 1.3 | 当日销售统计（`sales`/`newday`、持久化） | ⬜ 未开始 |
| Level 2.1 | 管理员价格管理 | ⬜ 未开始 |
| Level 2.2 | 管理员库存管理 | ⬜ 未开始 |
| Level 3 | 自由发挥（打折 / 报表 / 图表） | ⬜ 未开始 |

## 怎么编译

本仓库自带一份免安装的 GCC 14.1.0（`_tools/toolchain/w64devkit`），所以**不需要**先装 MinGW。

```powershell
# 编译并运行 hello world
.\build.cmd

# 通用编译（任何 .c 文件）
.\cc.cmd -Wall -o pos.exe src\pos.c
.\pos.exe
```

> `cc.cmd` 会自动把工具链的 `bin` 目录加进 `PATH`。
> 如果你手动调 `gcc.exe`，必须自己先加 `PATH`，否则会报
> `cannot execute 'as': CreateProcess: No such file or directory`。

在 Linux / macOS / WSL 上直接：

```bash
gcc -Wall -o pos src/pos.c && ./pos
```

## 怎么运行

```powershell
.\pos.exe
> 001
Cola 3.50
> prices
Item No. Pri.
-----------------
Cola 001 3.50
Lollipop 002 0.50
Noodles 003 6.00
> exit
```

## 目录结构

```
.
├── src/                    # 源码（pos.c 等）
├── data/                   # items.csv / sales.csv 等运行时数据
├── learning/               # 学习日志、路线图、hello world 练习
├── build.cmd / cc.cmd      # 编译脚本
├── _tools/                 # 本地工具链（已 gitignore）
└── 2026团队秋招大一题.pdf   # 原始题目
```

## 开发约定

- 编译永远带 `-Wall`，警告要清零。
- 一个功能一个 commit，message 写清楚做了什么（见 `learning/学习日志.md`）。
- 所有用户输出走英文（题目提示：Windows 中文编码很坑）。
- 金额一律用 `double` 打印 `%.2f`；不写浮点数相等比较（`a == b`），要用误差范围。
