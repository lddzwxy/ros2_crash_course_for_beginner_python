# 0.4 apt、软件源与国内镜像

> 模块 0 第 4 集 
> 前置：已完成 0.3，会用 `sudo` 和 `nano` 改文件。

---

## 一、本集目标

把 apt 源换成**国内镜像**（套件 `noble`），做到：

```bash
sudo apt update
sudo apt install -y tree htop
```

流畅不超时、不 404。

---

## 二、效果演示

对比同一个安装命令：

```bash
sudo apt install -y tree
```

- 换源前：进度条龟速，甚至 `Connection timed out`；
- 换源后：几秒下载完，直接装好。

**最终现象**：`sudo apt update` 全部 Hit/Get，域名是你选的镜像站（如 `mirrors.tuna.tsinghua.edu.cn`）。

---

## 三、理论讲解

### 3.1 apt 是什么？

Ubuntu 的**包管理器**。类比手机应用商店：

| 操作 | 命令 | 比喻 |
| ---- | ---- | ---- |
| 刷新商店列表 | `sudo apt update` | 下拉刷新 |
| 升级已装软件 | `sudo apt upgrade -y` | 全部更新 |
| 装新软件 | `sudo apt install -y <包>` | 下载安装 |
| 查包信息 | `apt policy <包>` | 看版本来源 |
| 搜索包 | `apt search <关键字>` | 商店搜索 |

**重要区分**：

- `apt update` = 只刷新**索引**（有哪些包、什么版本）；
- `apt upgrade` = 真正**升级已安装**的包；
- `apt install` = **安装**新包。

### 3.2 源配置在哪里？

Ubuntu 24.04 用 deb822 格式，主配置在：

```text
/etc/apt/sources.list.d/ubuntu.sources
```

里面有类似字段：

```text
Types: deb
URIs: http://archive.ubuntu.com/ubuntu/
Suites: noble noble-updates noble-security
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
```

### 3.3 为什么必须是 noble？

| Ubuntu 版本 | 代号 | 源里 Suites 要写 |
| ----------- | ---- | ---------------- |
| 22.04 | jammy | `jammy` 等 |
| **24.04** | **noble** | **`noble` `noble-updates` `noble-security`** |

源和系统版本不匹配 → `apt update` 报 404 或依赖错乱。**看见 jammy 就是错的**。

### 3.4 国内镜像站（选一个）

| 镜像站 | URI |
| ------ | --- |
| 清华 | `https://mirrors.tuna.tsinghua.edu.cn/ubuntu/` |
| 阿里云 | `https://mirrors.aliyun.com/ubuntu/` |
| 中科大 | `https://mirrors.ustc.edu.cn/ubuntu/` |

只把 `URIs:` 一行换成镜像站，**其它结构保持不动**。

### 3.5 改配置前先备份

铁律：

```bash
sudo cp 原文件 原文件.bak
```

改坏了随时覆盖回去。

---

## 四、实操步骤（手把手）

### 步骤 0 · 打开终端

Windows Terminal → **Ubuntu**（或开始菜单 → Ubuntu）。

**预期**：提示符 `laoding@DING-PC:~$` 。

### 步骤 1 · 确认系统版本

```bash
lsb_release -a
```

> 工作目录：任意。

**预期**：`Description: Ubuntu 24.04.x LTS`，`Codename: noble`。

### 步骤 2 · 备份原配置

```bash
sudo cp /etc/apt/sources.list.d/ubuntu.sources /etc/apt/sources.list.d/ubuntu.sources.bak
ls -l /etc/apt/sources.list.d/
```

**预期**：目录里同时有 `ubuntu.sources` 和 `ubuntu.sources.bak`。

### 步骤 3 · 查看原文件

```bash
cat /etc/apt/sources.list.d/ubuntu.sources
```

**预期**：能看到 `Types:` / `URIs:` / `Suites:` / `Components:` 等字段；`Suites` 含 `noble`。

### 步骤 4 · 改成国内镜像

用  `nano` 打开：

```bash
sudo nano /etc/apt/sources.list.d/ubuntu.sources
```

> `nano` 速查：`Ctrl+O` 保存 → 回车确认 → `Ctrl+X` 退出。

把每一处 `URIs:` 的域名换成镜像站（以清华为例），**只改域名**，例如：

```text
Types: deb
URIs: https://mirrors.tuna.tsinghua.edu.cn/ubuntu/
Suites: noble noble-updates noble-security
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
```

如果文件里有多段（比如还有源码 `deb-src`），每段的 `URIs` 都改成同一个镜像站。

**预期**：`Suites` 仍是 `noble` 开头；`URIs` 是镜像站域名；缩进/字段名没被改乱。

### 步骤 5 · 刷新索引

```bash
sudo apt update
```

**预期**：全部 `Hit` 或 `Get`，下载域名是镜像站；**没有** `Failed` / `404 Not Found`。

### 步骤 6 · 试装软件

```bash
sudo apt install -y tree htop vim
```

**预期**：下载速度明显快；安装结束无报错。

### 步骤 7 · 验证安装

```bash
tree --version
htop --version
apt policy tree
```

> `htop` 运行一次按 `q` 退出。

**预期**：版本号正常打印；`apt policy tree` 的 500 优先级来源含你选的镜像站。

### 步骤 8 · （可选）升级已装包

```bash
sudo apt upgrade -y
```

**预期**：列出可升级包并完成；无配置文件交互卡住（若有提问，一般选默认/保留）。

---

## 五、关键 API / 命令详解

| 命令 | 作用 | 备注 |
| ---- | ---- | ---- |
| `sudo apt update` | 刷新包索引 | 改源后必做 |
| `sudo apt upgrade -y` | 升级已装包 | `-y` 自动确认 |
| `sudo apt install -y <包>` | 安装包 | 最常用 |
| `apt search <词>` | 搜索 | 不需要 sudo |
| `apt policy <包>` | 看版本与来源 | 查是哪个源给的 |
| `sudo cp file file.bak` | 备份配置 | 改系统文件前必做 |
| `nano <file>` | 终端编辑器 | `Ctrl+O` 保存，`Ctrl+X` 退出 |
| `lsb_release -a` | 看系统代号 | 确认 noble |

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| `apt update` 报 `404 Not Found` | Suites 写成别的版本代号 | 全部改成 `noble` / `noble-updates` / `noble-security` |
| `E: Unable to locate package tree` | 没 update 直接 install | 先 `sudo apt update` |
| 改坏 `ubuntu.sources` 后 apt 全挂 | 格式改错 / 字段丢失 | `sudo cp ubuntu.sources.bak ubuntu.sources` 覆盖回去 |
| 复制镜像站配置后格式错乱 | 多删/多加了空行或字段名 | 保持与原文件相同的 `Types/URIs/Suites/Components` 结构 |
| `Permission denied` 改不了源文件 | 没加 `sudo` | `sudo nano ...` |
| 一直 `Connection timed out` | 网络问题或默认官方源太远 | 换镜像站；确认能上网 |
| `dpkg` 被占用 `Could not get lock` | 另一个 apt 在跑 | 等它结束，或 `sudo rm /var/lib/dpkg/lock-frontend` 后重试 |

---

## 七、预期输出汇总

1. `lsb_release -a` 是 24.04 / noble；
2. `sudo apt update` 全部 Hit/Get，域名是镜像站，无 Failed；
3. `tree`、`htop`、`vim` 安装成功并能运行；
4. `apt policy tree` 能看到镜像来源。

---

## 八、小作业（5 分钟）

1. 换成你常用的镜像站（清华 / 阿里 / 中科大任一）；
2. 安装 `htop` 并运行一次（按 `q` 退出）；
3. 把你改后的 `URIs:` 一行抄进笔记。

---

## 九、下集预告

软件装得动了。下集配一个舒服的写代码环境：**VS Code + WSL + 中文界面**。
