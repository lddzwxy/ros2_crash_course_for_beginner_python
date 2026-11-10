# 1.2 安装 ROS2 Jazzy

> 模块 1 第 2 集（安装类） 
> 前置：已完成模块 0；Ubuntu 24.04（noble）/ WSL2 正常。

---

## 一、本集目标

装好 **ROS2 Jazzy**，满足：

1. 新终端直接敲 `ros2 --help` 有输出；
2. `printenv ROS_DISTRO` 为 `jazzy`；
3. `ros2 doctor` 无致命错误；
4. source 已写入 `~/.bashrc`。

---

## 二、效果演示

**完全新开**一个 Ubuntu 终端，直接敲：

```bash
ros2 --help
```

**最终现象**：列出一大串子命令（`daemon`、`node`、`pkg`、`topic` ……）。

不手动 source 也有——说明环境配置成功。这就是本集终点。

---

## 三、理论讲解

### 3.1 我们要装什么？

| 组件 | 作用 |
| ---- | ---- |
| ROS2 **Jazzy Jalisco** | 发行版本体（LTS） |
| `ros-jazzy-desktop` | 桌面全家桶：核心 + 常用工具 + 仿真相关库 |
| `python3-colcon-common-extensions` | 构建工具 colcon（下下集用） |
| `python3-rosdep` | 按 `package.xml` 装依赖 |
| `python3-vcstool` | 批量拉代码 |
| `python3-argcomplete` | `ros2` 命令补全 |

apt 包名前缀固定 **`ros-jazzy-*`**。看到别的前缀就说明文档版本不对。

### 3.2 为什么先设 locale？

ROS2 期望 **UTF-8** 环境。locale 不对时，可能报奇怪的编码错误。

```bash
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
```

### 3.3 为什么要加 ROS2 软件源？

Ubuntu 官方源里没有 `ros-jazzy-*`。需要把 **packages.ros.org** 的源加进 apt，并导入官方 GPG 密钥，才能验证包的完整性。

### 3.4 source 是什么？

安装完的 ROS2 在 `/opt/ros/jazzy`。要让 `ros2` 命令可用，必须加载它的环境脚本：

```bash
source /opt/ros/jazzy/setup.bash
```

它会设置 `PATH`、`AMENT_PREFIX_PATH`、`ROS_DISTRO` 等环境变量。

写进 `~/.bashrc` 后，**每次开新终端自动生效**。

### 3.5 rosdep 是什么？

每个包的 `package.xml` 写了"我依赖什么"。**rosdep** 负责把这些依赖映射到 apt 包并安装。后面建包、编译前经常用它。

### 3.6 版本锁死

| 项 | 值 |
| -- | -- |
| Ubuntu | 24.04 LTS（`noble`） |
| ROS2 | **Jazzy Jalisco** |
| Python | **3.12** |
| apt 前缀 | `ros-jazzy-*` |

---

## 四、实操步骤（手把手）

### 步骤 0 · 打开终端

Windows Terminal → **Ubuntu**（或开始菜单 → Ubuntu）。

**预期**：提示符 `<用户名>@<电脑名>:~$`。

### 步骤 1 · 更新软件包索引

```bash
sudo apt update && sudo apt upgrade -y
```

> 工作目录：任意。

**预期**：索引刷新成功；若有升级会自动装完，无 Failed。

### 步骤 2 · 安装基础工具

```bash
sudo apt install -y software-properties-common curl gnupg lsb-release
```

**预期**：安装完成，无报错。

### 步骤 3 · 设置 locale（UTF-8）

```bash
sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
```

执行完后**重开一个终端**再继续（让 locale 生效）。

**预期**：`locale` 命令输出中 `LANG` 含 `UTF-8`。

### 步骤 4 · 启用 universe 仓库并添加 ROS2 apt 源

```bash
sudo add-apt-repository universe
sudo apt update && sudo apt install -y curl gnupg lsb-release
# 使用清华镜像下载密钥
sudo curl -sSL https://mirrors.tuna.tsinghua.edu.cn/rosdistro/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
# 添加清华 ROS2 源
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu noble main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

> 这段做的事：① 开 universe；② 导入官方 GPG 密钥；③ 写入 `ros2.list`，套件自动取 `noble`。

**预期**：

- `cat /etc/apt/sources.list.d/ros2.list` 能看到 `mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu` 与 `noble`；
- `/usr/share/keyrings/ros-archive-keyring.gpg` 文件存在。

### 步骤 5 · 刷新索引

```bash
sudo apt update
```

**预期**：出现 `mirrors.tuna.tsinghua.edu.cn` 的 Hit/Get，无 `404`、无 `NO_PUBKEY`。

### 步骤 6 · 安装 ROS2 Jazzy 与工具链

```bash
sudo apt install -y ros-jazzy-desktop python3-colcon-common-extensions python3-rosdep python3-vcstool python3-argcomplete
```

> 这一步下载量很大（几 GB），视网络情况 10–30 分钟。保持终端不关。

**预期**：安装完成；`dpkg -l | grep ros-jazzy-desktop` 能看到 `ii` 状态。

### 步骤 7 · 写入 bashrc 并生效

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

**预期**：`printenv ROS_DISTRO` 输出

```text
jazzy
```

### 步骤 8 · 初始化 rosdep

`rosdep init` 的核心是创建 `/etc/ros/rosdep/sources.list.d/20-default.list` 文件，我们可以手动创建它并指向国内镜像。

```bash
# 手动创建目录和文件
sudo mkdir -p /etc/ros/rosdep/sources.list.d/
# 将国内镜像的 20-default.list 下载到指定位置
sudo curl -L -o /etc/ros/rosdep/sources.list.d/20-default.list https://mirrors.bfsu.edu.cn/github-raw/ros/rosdistro/master/rosdep/sources.list.d/20-default.list
# 为 rosdep update 换源并更新
export ROSDISTRO_INDEX_URL=https://mirrors.bfsu.edu.cn/rosdistro/index-v4.yaml
rosdep update
```

**预期**：`rosdep update` 最后提示更新成功（Wrote / updated 之类）。

### 步骤 9 · 验证

```bash
ros2 --help
ros2 doctor
printenv ROS_DISTRO
python3 --version
```

**预期**：

1. `ros2 --help` 列出子命令；
2. `ros2 doctor` 打印检查报告（允许少量 Warning，**无致命 Error**）；
3. `ROS_DISTRO=jazzy`；
4. `python3` 为 3.12.x。

### 步骤 10 · 开新终端再验一次

再开一个 Ubuntu 终端，**不要手动 source**，直接：

```bash
ros2 pkg list
```

**预期**：能列出一堆 ROS2 包名。

---

## 五、关键 API / 命令详解

| 命令 | 作用 |
| ---- | ---- |
| `sudo locale-gen en_US en_US.UTF-8` | 生成 UTF-8 locale |
| `sudo add-apt-repository universe` | 启用 universe 仓库 |
| `curl ... ros.key -o .../ros-archive-keyring.gpg` | 导入 ROS2 官方 GPG 密钥 |
| `echo "deb ..." \| sudo tee /etc/apt/sources.list.d/ros2.list` | 写入 ROS2 apt 源 |
| `sudo apt install ros-jazzy-desktop` | 安装 ROS2 Jazzy 桌面版 |
| `source /opt/ros/jazzy/setup.bash` | 加载 ROS2 环境 |
| `echo "source ..." >> ~/.bashrc` | 开机自动加载 |
| `sudo rosdep init && rosdep update` | 初始化并更新依赖数据库 |
| `ros2 doctor` | 环境体检 |
| `printenv ROS_DISTRO` | 查看当前 ROS 发行版 |
| `ros2 pkg list` | 列出已发现的 ROS2 包 |

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| `ros2: command not found` | 没 source 或没写 bashrc | `source /opt/ros/jazzy/setup.bash`；检查 `~/.bashrc` |
| `printenv ROS_DISTRO` 不是 `jazzy` | 装错发行版 / 文档没切到 Jazzy | 只用 `ros-jazzy-*`；确认源是 `noble` |
| `apt update` 报 `404 Not Found` | ROS 源套件与系统不匹配 | 确认 `ros2.list` 里是 `noble` |
| `NO_PUBKEY` / `GPG error` | 密钥没导入或路径错 | 重跑步骤 4 的 `curl ... ros.key` 那行 |
| `ros2 doctor` 一堆 Error | 环境混杂 / 没 source | 新开终端；只 source 一次 `/opt/ros/jazzy` |
| `rosdep init` 报 `already initialized` | 已初始化过 | 跳过，只执行 `rosdep update` |
| `rosdep update` 很慢/超时 | 网络到 GitHub 慢 | 多试几次；或稍后在 `ros2_ws` 里用 `rosdep install` |
| 安装中断 / `dpkg` 被占用 | 同时开了别的 apt | 等其结束；`sudo apt --fix-broken install` |

---

## 七、预期输出汇总

1. `ros2 --help` 有完整帮助；
2. `printenv ROS_DISTRO` = `jazzy`；
3. `python3 --version` = 3.12.x；
4. `ros2 doctor` 无致命错误；
5. 新终端不手动 source 也能跑 `ros2`。

---

## 八、小作业（5 分钟）

1. **故意**开一个不加载 ROS 环境的终端（临时屏蔽）：

```bash
env -i bash --noprofile --norc
ros2 --help
```

2. 观察 `ros2: command not found`；
3. 执行 `source /opt/ros/jazzy/setup.bash` 后恢复正常；
4. 把"为什么必须 source"一句话写进笔记。

---

## 九、下集预告

装好了。下集用 **turtlesim 乌龟** 真正发号施令，学会 `ros2 run / node / topic / param` 核心命令。
