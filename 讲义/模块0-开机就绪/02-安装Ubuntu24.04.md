# 0.2 安装 Ubuntu 24.04（WSL2）

> 模块 0 第 2 集 
> 前置：已完成 0.1；Windows 11 或 Windows 10 21H2+，虚拟化已启用。

---

## 一、本集目标

装好 **WSL2 + Ubuntu 24.04**，满足：

1. `wsl -l -v` 显示 `Ubuntu-24.04` 且 **VERSION = 2**；
2. Ubuntu 终端能正常输入命令；
3. WSLg 能弹出 Linux 图形窗口。

---

## 二、效果演示

在 Ubuntu 终端里敲一行：

```bash
xeyes
```

**最终现象**：Windows 桌面上弹出一个小窗口，两只黑眼睛**跟着你的鼠标转**。

这是 Linux GUI 跑在 Windows 里——WSLg 的图形转发。看到小眼睛，这一集就成了。

---

## 三、理论讲解

### 3.1 我们要装的是什么？

你的电脑是 Windows，但 ROS2 的"主场"是 Ubuntu。安装Ubuntu的方式：

- **独立安装**：性能最佳，适合专用 Linux 设备。
- **双系统**：兼顾 Windows 和 Ubuntu，适合日常混合使用。
- **虚拟机**：安全、易恢复，适合学习和测试。
- **WSL**：快速、轻量，适合开发者和命令行操作。

**WSL2**（Windows Subsystem for Linux 2）= 在 Windows 里跑一个**真正的 Linux 内核**。

| 概念         | 是什么                   | 生活比喻                     |
| ------------ | ------------------------ | ---------------------------- |
| **WSL2**     | 跑真 Linux 内核 + 虚拟机 | 小屋是真砖房                 |
| **WSLg**     | WSL2 的图形转发          | 小屋的窗户，能看见里面画面   |
| Ubuntu 24.04 | 里头的 Linux 发行版      | 小屋里住的人（代号 `noble`） |

我们只用 **WSL2**。它才是真 Linux，后面的 ROS2、仿真都靠它。

### 3.2 Windows 命令 vs Ubuntu 命令

这是新手最大的混淆点。同一个"终端"，**两边命令完全不同**：

| 你在哪 | 提示符长什么样 | 能敲什么 |
| ------ | -------------- | -------- |
| Windows PowerShell | `PS C:\Users\<用户名>` | `wsl`、`notepad`、`ipconfig` |
| Ubuntu 终端 | `<用户名>@<电脑名>:~$` | `sudo apt`、`ros2 -h` |

**口诀**：管理 WSL 用 PowerShell（Windows 侧），干活用 Ubuntu 终端（Linux 侧）。

### 3.3 为什么要 `.wslconfig`？

WSL2 默认会尽量多吃内存。给它划个界：

```text
[wsl2]
memory=4GB
processors=4
```

这样 Windows 侧还留得住力气，两边都不卡。

### 3.4 发行版代号：noble

Ubuntu 24.04 的代号是 **noble**。后面配软件源时，套件名必须写 `noble`，写成别的代号会 404。

---

## 四、实操步骤（手把手）

### 步骤 0 · 打开 Windows PowerShell（管理员）

1. 鼠标移至开始菜单右击，选择 `终端(管理员)`，或者按 `Win + X` 键，再按 `A` 键；
2. 若弹出 UAC（用户账户控制），点"是"。

**预期**：出现一个（蓝色）窗口，标题含"管理员"，提示符类似 `PS C:\Users\<用户名>`。

### 步骤 1 · 一键安装 Ubuntu 24.04

在 PowerShell 里**完整复制**执行：

```powershell
# 更新WSL内核
wsl --update
# 安装 Ubuntu 24.04
wsl --install -d Ubuntu-24.04
```

> 工作目录：Windows 任意目录均可（此命令不依赖当前路径）。

耐心等待下载（几百 MB）。中途可能要求**重启电脑**。

**预期**：提示安装成功；或提示重启。若提示重启，请重启后继续步骤 2。

### 步骤 2 · 设置 Ubuntu 用户名和密码

重启后会自动弹出 Ubuntu 窗口（黑底白字），显示：

```text
Please create a default UNIX user account.
Enter new UNIX username:
```

依次输入：

1. **用户名**：建议**英文小写**，如 `laoding`（避免中文/空格）；
2. **密码**：输入时**屏幕不显示任何字符**，盲打后回车；
3. **再输一遍密码**确认。

**预期**：出现类似 `laoding@<电脑名>:~$` 的提示符，说明 Ubuntu 用户建好了。

> 忘记密码也没关系：在 Windows PowerShell 里执行 `wsl -d Ubuntu-24.04 -u root`，再用 `passwd <用户名>` 重置，或重置发行版。先记在笔记里。

### 步骤 3 · 回到 Windows 验证 WSL2

切换回 **Windows PowerShell**（不需要管理员也可以），执行：

```powershell
wsl -l -v
```

**预期**：看到类似

```text
  NAME            STATE           VERSION
* Ubuntu-24.04    Running         2
```

关键两点：NAME 是 `Ubuntu-24.04`，VERSION 是 **2**。

### 步骤 4 · （仅当 VERSION 不是 2）转换为 WSL2

```powershell
wsl --set-version Ubuntu-24.04 2
wsl --set-default-version 2
```

> 第一条会花一两分钟转换。**不要中途关窗口**。

**预期**：`wsl -l -v` 再次确认 VERSION = 2。

### 步骤 5 · 确认系统版本

回到 **Ubuntu 终端**：

```bash
lsb_release -a
```

**预期**：输出含

```text
Description:    Ubuntu 24.04.x LTS
Codename:       noble
```

如果不是 24.04 / noble，说明装错发行版，回到步骤 1 用 `-d Ubuntu-24.04` 重装。

### 步骤 6 · 配置 `.wslconfig` 限制资源

回到 **Windows PowerShell**，编辑（或创建）用户目录下的 `.wslconfig`：

```powershell
notepad "$env:USERPROFILE\.wslconfig"
```

在打开的记事本里写入：

```ini
[wsl2]
memory=4GB
processors=4
```

保存关闭。然后让 WSL 完全退出再进：

```powershell
wsl --shutdown
```

再从开始菜单打开 **Ubuntu**。

**预期**：Ubuntu 能正常重新进入；`free -h` 里 total 约 4 GB。

### 步骤 7 · WSLg 图形验证：小眼睛

在 **Ubuntu 终端**执行：

```bash
sudo apt update
sudo apt install -y x11-apps
xeyes
```

（`sudo` 会要密码，就是步骤 2 设的那个，盲打回车。）

**预期**：Windows 桌面弹出小眼睛窗口，黑眼珠跟着鼠标转。按 `Ctrl+C` 关闭。

### 步骤 8 · 关掉再打开，数据还在

1. 关闭 Ubuntu 窗口；
2. 开始菜单 → 搜索 **Ubuntu** → 打开；
3. `pwd`、`ls` 看看家目录。

**预期**：用户名还在，文件还在。WSL 的数据是持久的。

---

## 五、关键 API / 命令详解

| 命令 | 作用 | 在哪敲 |
| ---- | ---- | ------ |
| `wsl --install -d Ubuntu-24.04` | 安装指定发行版 | Windows PowerShell |
| `wsl -l -v` | 列出已装发行版和 WSL 版本 | Windows PowerShell |
| `wsl --set-version Ubuntu-24.04 2` | 把发行版转成 WSL2 | Windows PowerShell |
| `wsl --set-default-version 2` | 以后默认装 WSL2 | Windows PowerShell |
| `wsl --shutdown` | 完全关闭 WSL（改内存后必做） | Windows PowerShell |
| `wsl --update` | 更新 WSL 内核 / WSLg | Windows PowerShell |
| `lsb_release -a` | 查看 Ubuntu 版本与代号 | Ubuntu 终端 |
| `sudo apt install -y <包>` | 安装软件包（要密码） | Ubuntu 终端 |
| `xeyes` | WSLg 图形小测试 | Ubuntu 终端 |
| `free -h` | 查看内存 | Ubuntu 终端 |

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| `wsl -l -v` 的 VERSION 是 1 | 装成了 WSL1 | `wsl --set-version Ubuntu-24.04 2` |
| `xeyes` 无窗口 / 黑窗 | WSLg 未就绪 | `wsl --update`；确认 Windows 10 21H2+ 或 Win11 |
| PowerShell 报"无法识别 wsl" | Windows 太旧或未启用虚拟机平台 | 进 BIOS 开虚拟化；Windows 更新到 21H2+ |
| 在 PowerShell 里敲 `ls` / `cd` 报"不是内部或外部命令" | 在错的终端里敲 Linux 命令 | 先进 Ubuntu 终端再敲 |
| 中文用户名导致路径乱码 | 用户名含中文/空格 | 用英文用户名；严重时重装发行版 |
| `sudo` 输密码屏幕没反应 | 正常盲打 | 输完直接回车 |
| `apt` 报网络错误 | 软件源未换国内镜像 | 本集先跳过，下一集换源 |

---

## 七、预期输出汇总

1. `wsl -l -v` 显示 `Ubuntu-24.04` / `Running` / **`2`**；
2. `lsb_release -a` 含 `Ubuntu 24.04` 与 `noble`；
3. `xeyes` 弹出小眼睛窗口，跟鼠标；
4. 关开 Ubuntu 窗口，用户和文件都还在。

---

## 八、小作业（5 分钟）

1. 截图 `wsl -l -v` 的输出；
2. 截图 `xeyes` 小眼睛窗口；
3. 关掉 Ubuntu 窗口再从开始菜单打开，确认用户和文件还在，把结果写进笔记。

---

## 九、下集预告

系统有了。下集学**Linux 命令行急救包**：目录、权限、进程、管道——在黑窗口里活下来。
