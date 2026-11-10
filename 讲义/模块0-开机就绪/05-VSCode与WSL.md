# 0.5 VS Code + WSL + 中文

> 模块 0 第 5 集 
> 前置：已完成 0.2–0.4；Ubuntu 24.04 / WSL2 正常。

---

## 一、本集目标

Windows 的 **VS Code** 经 **WSL 扩展**连进 Ubuntu，做到：

1. 标题栏出现 `"WSL: Ubuntu-24.04"`；
2. VS Code 里的终端就是 Ubuntu bash；
3. Python 3.12 插件可用；
4. 界面中文。

---

## 二、效果演示

VS Code 左侧文件树打开 `~/dev/practice`，右侧新建 `hello.py`：

```python
print("hello vscode")
```

点右上角 ▶ 运行。

**最终现象**：下方终端打印 `hello vscode`，而这个终端里 `uname -a` 是 Linux。

Windows 的编辑体验 + Ubuntu 的运行环境，就是我们后面写 ROS2 的标准姿势。

---

## 三、理论讲解

### 3.1 东西各装在哪？

| 组件 | 装在哪 | 作用 |
| ---- | ------ | ---- |
| VS Code | **Windows** | 编辑器本体 |
| 代码文件 | **WSL/Ubuntu** | 在 Linux 磁盘上 |
| 终端 | **WSL/Ubuntu** | 编译运行都在这 |
| Remote-WSL扩展 | 桥梁 | 让 VS Code 连进 WSL |
| Python 扩展 | **WSL 侧** | 找 Linux 的 python3 |
| Chinese 语言包 | 界面 | 只影响显示语言 |

**核心**：VS Code 装在 Windows，但**代码和终端在 Linux**。中间靠 Remote - WSL 这座桥。

### 3.2 为什么要区分"装在 Windows"还是"装在 WSL"？

扩展分两边。装错边的典型症状：

- Python 扩展装在 Windows → 它找的是 Windows 的 Python，找不到 WSL 的 3.12；
- 装在 WSL → 显示"Install in WSL: Ubuntu-24.04"，一切正常。

**看扩展页按钮上的小字**，是判断装哪边的最快方法。

### 3.3 中文语言包只改界面

`Chinese (Simplified) Language Pack` 只把菜单/按钮变中文，**不改变**代码、终端输出的语言。装完要**重启 VS Code** 才生效。

### 3.4 VS Code 里的终端 = Ubuntu bash

左下角或 `Ctrl+~`  打开的终端，提示符应是 `laoding@DING-PC:~`。在这里敲 `uname -a`，出来的是 Linux 内核信息。

---

## 四、实操步骤（手把手）

### 步骤 0 · 打开 Windows 桌面

本集大部分操作在 Windows 图形界面，最后一段回 Ubuntu。

**预期**：能上网下载软件。

### 步骤 1 · Windows 侧安装 VS Code

浏览器打开 `code.visualstudio.com`，下载 **User Installer** 或 **System Installer**，一路下一步装完。

**预期**：开始菜单能搜到 **Visual Studio Code** 并打开。

### 步骤 2 · 安装 WSL 扩展（Windows 侧）

1. VS Code 左侧点**扩展**图标（`Ctrl+Shift+X`）；
2. 搜索 `WSL`；
3. 安装 **WSL**（发布者 Microsoft，ID：`ms-vscode-remote.remote-wsl`）。

**预期**：扩展显示"卸载/禁用"按钮，表示已装好。

### 步骤 3 · 从 Ubuntu 终端用 `code .` 打开

打开 **Ubuntu 终端**：

```bash
cd ~/dev/practice
code .
```

> 工作目录：`~/dev/practice`（0.3 建好的练习目录）。

第一次运行可能稍等几秒，它会自动装 WSL 侧的 Server。

**预期**：弹出 VS Code，**标题栏**含有 `"WSL: Ubuntu-24.04"`。

> 若 `code` 命令不存在：完全关闭并重开 Ubuntu 终端再试；或从 VS Code 左下角 → **Connect to WSL**。

### 步骤 4 · 在 WSL 窗口里装 Python 与中文包

确认窗口标题有 `"WSL: Ubuntu-24.04"` 后，打开扩展页（`Ctrl+Shift+X`），安装：

1. **Python**（`ms-python.python`）——按钮旁应显示 **Install in WSL: Ubuntu-24.04**；
2. **Chinese (Simplified) Language Pack for Visual Studio Code**（`ms-ceintl.vscode-language-pack-zh-hans`）。

**预期**：

- Python 扩展状态为装在 WSL；
- 右下角可能提示"需要重新加载/重启"。

### 步骤 5 · 重启 VS Code 并验证环境

关闭 VS Code 全部窗口，重新 `code .` 打开。

在 VS Code 内置终端（`Ctrl+` `` ` ``）执行：

```bash
uname -a
python3 --version
```

**预期**：

- `uname -a` 含 `Linux`；
- `python3 --version` 为 `Python 3.12.x`；
- 界面菜单已是中文（若还不是，再重启一次）。

### 步骤 6 · 写并运行 hello.py

在资源管理器新建文件 `hello.py`（路径 `~/dev/practice/hello.py`）：

```python
# ~/dev/practice/hello.py
# 练习：VS Code + WSL 运行第一个脚本
print("hello vscode")
```

保存（`Ctrl+S`），点右上角 **运行**（▶），或在终端：

```bash
cd ~/dev/practice
python3 hello.py
```

**预期**：输出

```text
hello vscode
```

### 步骤 7 · （对照）打印当前时间的小脚本

再新建 `print_time.py`，内容与仓库 `code/m0_setup/practice_python/print_time.py` 一致：

```python
#!/usr/bin/env python3
# 练习：打印当前时间（模块0 小作业）
# 运行: python3 print_time.py

from datetime import datetime


def main():
    now = datetime.now()
    print('当前时间:', now.strftime('%Y-%m-%d %H:%M:%S'))
    print('这是 ROS2 课程的第一个 Python 脚本，干得漂亮！')


if __name__ == '__main__':
    main()
```

运行：

```bash
python3 print_time.py
```

**预期**：打印当前日期时间和鼓励语。

---

## 五、关键 API / 命令详解

| 名称 | 作用 |
| ---- | ---- |
| `code .` | 用 VS Code 打开当前目录（从 Ubuntu 终端敲） |
| WSL 扩展 `ms-vscode-remote.remote-wsl` | 桥接 Windows VS Code 与 WSL |
| Python 扩展 `ms-python.python` | 语法高亮、运行、调试；必须装在 WSL 侧 |
| 中文包 `ms-ceintl.vscode-language-pack-zh-hans` | 界面汉化 |
| `uname -a` | 显示内核信息，用来确认"这是 Linux" |
| `python3 --version` | 确认 Python 3.12 |
| `datetime.now()` | 取当前时间 |
| `strftime('%Y-%m-%d %H:%M:%S')` | 把时间格式化成字符串 |
| `if __name__ == '__main__':` | 脚本直接运行时才执行 `main()` |

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| 标题栏没有 `"WSL: Ubuntu-24.04"`，终端是 PowerShell、路径是 `C:\...` | 没走 WSL 远程 | 从 Ubuntu 终端 `code .` 打开；或左下角 Connect to WSL |
| Python 扩展找不到解释器 | 插件装在 Windows 侧 | 在 WSL 窗口扩展页重装 Python，确认"Install in WSL" |
| `code: command not found` | 命令未进 PATH | 重开 Ubuntu 终端；或用 Connect to WSL |
| 中文没生效 | 未重启 VS Code | 关掉所有窗口重开 |
| 用资源管理器改 `\\wsl$\...` 文件不同步 | 跨系统编辑偶发延迟 | 统一在 VS Code WSL 窗口里改 |
| 运行按钮点了没反应 | 未选对解释器 | 右下角选择 `/usr/bin/python3` |
| `python3: command not found` | 在 Windows 终端敲的 | 切到 Ubuntu / WSL 终端 |

---

## 七、预期输出汇总

1. VS Code 标题栏含 `"WSL: Ubuntu-24.04"`；
2. 内置终端 `uname -a` 是 Linux，`python3 --version` 是 3.12.x；
3. `hello.py` 运行打印 `hello vscode`；
4. `print_time.py` 运行打印当前时间。

---

## 八、小作业（5 分钟 · 本模块主作业）

用 VS Code 打开 `~/dev/practice`，写一个**打印当前时间**的脚本并跑通：

```bash
cd ~/dev/practice
python3 print_time.py
```

把运行截图和输出贴进笔记。可以对照仓库里的 `code/m0_setup/practice_python/print_time.py`。

---

## 九、下集预告

环境舒服了。下集用 **Python 3.12** 写第一个"机器人"小脚本：类、异常、主入口——给后面的 ROS2 节点打底。
