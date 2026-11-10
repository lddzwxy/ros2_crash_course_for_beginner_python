# 1.5 colcon 编译与排查

> 模块 1 第 5 集 
> 前置：已完成 1.4，`~/ros2_ws/src/my_first_pkg` 已创建。

---

## 一、本集目标

把 `my_first_pkg` **编译**成可运行的节点，完成：

`写代码 → 配置 → colcon build → source → ros2 run` 闭环。

---

## 二、效果演示

开一个新终端，输入：

```bash
ros2 run my_first_pkg hello_node
```

**预期**：屏幕上出现

```text
[INFO] [hello_node]: Hello ROS2
[INFO] [hello_node]: 欢迎来到 Jazzy + Python 3.12 之旅
```

这就是本集结束时你要做到的效果。

---

## 三、理论讲解

### 3.1 为什么需要 colcon？

你写的 Python 代码，ROS2 **不是**直接 `python3 hello_node.py` 跑的，而是：

1. 把包"安装"到 `install/` 目录（拷贝或符号链接）；
2. 把可执行入口注册到 `lib/<包名>/`；
3. 生成 `install/setup.bash`，让 `ros2` 命令能找到你的包。

**colcon** 就是干这件事的构建工具（Jazzy 标准，不用 catkin）。

### 3.2 目录在干什么

```text
~/ros2_ws/
├── src/          ← 你写的源码
├── build/        ← 编译中间产物（可删）
├── install/      ← 安装结果（source 这里的 setup.bash）
└── log/          ← 编译日志（出错先看这里）
```

### 3.3 `--symlink-install` 是什么？

默认 colcon 会把 `.py` **拷贝**到 `install/`，改源码要重新 build。 
加 `--symlink-install` 后建立**符号链接**，改 `.py` 通常**不用**重新 build（更推荐教学使用）。

### 3.4 必须 source 的原因

`ros2 run my_first_pkg ...` 依赖环境变量 `AMENT_PREFIX_PATH` 等。 
不 source，ROS2 **根本不知道**你装过这个包。

---

## 四、实操步骤（手把手）

### 步骤 0 · 打开终端

Windows：打开 **Windows Terminal**，下拉选择 **Ubuntu**； 
或按 `Ctrl+Shift+T` 新建 Ubuntu 标签页。

**预期**：出现类似 `<用户名>@<电脑名>:~$` 的提示符。

### 步骤 1 · 进入工作空间并查看包

```bash
cd ~/ros2_ws
find src/my_first_pkg -type f | sort
```

**预期**：至少看到

```text
src/my_first_pkg/package.xml
src/my_first_pkg/setup.py
src/my_first_pkg/setup.cfg
src/my_first_pkg/resource/my_first_pkg
src/my_first_pkg/my_first_pkg/__init__.py
src/my_first_pkg/my_first_pkg/hello_node.py
```

### 步骤 2 · 打开并确认 hello_node.py

用 VS Code 打开 `~/ros2_ws/src/my_first_pkg/my_first_pkg/hello_node.py`。

**为什么这么写（先讲动机）**：我们只需要一个"会说话的节点"，所以：

- 用类 `HelloNode` 继承 `Node`——这是 rclpy 标准写法，后面加话题/服务都方便；
- 在构造函数里 `super().__init__('hello_node')` 注册节点名；
- 用 `get_logger()` 而不是 `print`——日志有级别、能进 rqt_console；
- `main()` 负责 init / spin / shutdown 三件套。

完整代码（与仓库 `code/src/my_first_pkg/my_first_pkg/hello_node.py` 一致）：

```python
#!/usr/bin/env python3
# 第一个 ROS2 节点：向终端打印问候，并发布一条简单日志
# 教学点：继承 Node、构造节点名、日志、spin、main 入口

import rclpy
from rclpy.node import Node


class HelloNode(Node):
    """最小 ROS2 节点：启动即打印 Hello ROS2。"""

    def __init__(self):
        # 节点名 hello_node；可被 --ros-args -r __node:=xxx 覆盖
        super().__init__('hello_node')
        self.get_logger().info('Hello ROS2')
        self.get_logger().info('欢迎来到 Jazzy + Python 3.12 之旅')


def main(args=None):
    # 1) 初始化 rclpy 上下文（每个进程一次）
    rclpy.init(args=args)
    # 2) 创建节点实例
    node = HelloNode()
    try:
        # 3) spin：进入事件循环，处理回调（本例无定时器，Ctrl+C 退出）
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # 4) 释放资源
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

**预期**：文件能保存，语法无红线报错。

### 步骤 3 · 确认 setup.py 入口

打开 `setup.py`，找到：

```python
entry_points={
    'console_scripts': [
        'hello_node = my_first_pkg.hello_node:main',
    ],
},
```

含义：可执行名叫 `hello_node`，对应模块 `my_first_pkg.hello_node` 里的 `main` 函数。

**预期**：字符串三段与实际路径一致。

### 步骤 4 · 编译

```bash
cd ~/ros2_ws
colcon build --symlink-install
```

**预期**：末尾类似

```text
Starting >>> my_first_pkg
Finished <<< my_first_pkg [0.50s]
Summary: 1 package finished
```

若失败：看终端里的 **File "..." line N**，或 `less log/latest_build/my_first_pkg/stdout_stderr.log`。

### 步骤 5 · source 环境

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

> 日常可以把这两行写进 `~/.bashrc`，但**学习阶段建议手动 source**，培养肌肉记忆。

**预期**：`ros2 pkg list | grep my_first` 能列出 `my_first_pkg`。

### 步骤 6 · 确认可执行文件

```bash
ros2 pkg executables my_first_pkg
```

**预期**：

```text
my_first_pkg hello_node
```

### 步骤 7 · 运行节点

```bash
ros2 run my_first_pkg hello_node
```

**预期**：打印两条 Hello 日志。按 `Ctrl+C` 退出。

### 步骤 8 · 再开一个终端验证

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 node list
```

（在 hello_node 仍运行时）**预期**：看到 `/hello_node`。

---

## 五、关键 API / 命令详解

| 名称 | 作用 |
| ---- | ---- |
| `colcon build` | 构建工作空间内所有包 |
| `--symlink-install` | 用符号链接安装，改源码少重新编译 |
| `source install/setup.bash` | 把本工作空间加入 ROS 环境 |
| `ros2 run <包> <可执行>` | 运行已安装的节点 |
| `ros2 pkg executables` | 查看某包有哪些可执行 |
| `rclpy.init/shutdown` | 进程级初始化/清理 |
| `rclpy.spin(node)` | 事件循环，处理定时器与订阅回调 |
| `Node.get_logger()` | 节点日志（info/warn/error） |

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| `Package 'my_first_pkg' not found` | 没 source install 或没 build | 先 `colcon build`，再 source 两层 |
| `ros2: command not found` | 没 source `/opt/ros/jazzy` | `source /opt/ros/jazzy/setup.bash` |
| `Executable 'hello_node' not found` | entry_points 写错 / 没重编译 | 核对 setup.py，重新 build |
| `IndentationError` | 缩进混用 Tab/空格 | 全部用 4 空格（PEP8） |
| 改了 .py 行为没变 | 没用 symlink 或没重启进程 | `--symlink-install` + 重新 run |

---

## 七、预期输出汇总

1. `colcon build` Summary 成功；
2. `ros2 pkg executables my_first_pkg` 有 `hello_node`；
3. `ros2 run my_first_pkg hello_node` 打印 Hello；
4. `ros2 node list` 可见 `/hello_node`。

---

## 八、小作业（5 分钟）

1. 把打印改成自己的名字，例如 `Hello, 张三！`；
2. 由于用了 `--symlink-install`，**不重新 build**，直接再 `ros2 run`，确认改动生效；
3. 去掉 symlink 重新 `colcon build`，对比行为。

---

## 九、下集预告

你已经拥有第一个 ROS2 节点。接下来进入**模块 2**：节点之间如何通过 **Topic（话题）** 说话——从广播喻意，到手写 Publisher / Subscriber。
