# 2.2 节点 Node：名字、命名空间、重映射

> 模块 2 第 2 集 
> 前置：已完成 2.1；模块 1 已编译 `my_first_pkg`。

---

## 一、本集目标

理解节点 = 可执行进程里的"工作单位"，并会：

- 用 `ros2 node list / info` 查看节点；
- 改**节点名**（`__node:=`）；
- 加**命名空间**（`__ns:=`）；
- 理解"包名 / 可执行名 / 节点名"三者不是一回事。

---

## 二、效果演示

同一份 `hello_node` 程序，跑三次，名字各不相同：

```bash
ros2 run my_first_pkg hello_node
ros2 run my_first_pkg hello_node --ros-args -r __node:=hello2
ros2 run my_first_pkg hello_node --ros-args -r __ns:=/robot1 -r __node:=hello
```

**预期**：`ros2 node list` 看到三个不同身份：

```text
/hello_node
/hello2
/robot1/hello
```

同一个程序，三个"工牌"。

---

## 三、理论讲解

### 3.1 节点是什么

一个**节点**就是"一个会干某件具体事的执行单元"：

```text
hello_node          → 只负责打印问候
velocity_publisher  → 只负责发速度
velocity_subscriber → 只负责收速度
```

一个**进程**可以有多个节点，但入门阶段我们坚持"一个可执行 = 一个节点"，简单清晰。

### 3.2 三个名字，别搞混

| 名字 | 写在哪 | 例子 | 作用 |
| ---- | ------ | ---- | ---- |
| **包名** | `package.xml` / `setup.py` | `my_first_pkg` | 安装、编译、依赖的单位 |
| **可执行名** | `setup.py` 的 `entry_points` | `hello_node` | `ros2 run 包 可执行` 用的 |
| **节点名** | 代码里 `super().__init__('...')` | `hello_node` | 图上的身份，`ros2 node list` 看到的 |

三者可以同名（新手常见），但**概念完全不同**。

### 3.3 命名空间

命名空间像"部门"：同一个程序放到 `/robot1` 下，就变成 `/robot1/hello`。

用途：多机器人时，每个机器人一套 `/robot1/...`、`/robot2/...`，互不干扰。

### 3.4 重映射 remap

`--ros-args -r __node:=xxx` 是**不改代码**就换名字的标准手段。

```text
-r __node:=hello2     改节点名
-r __ns:=/robot1      改命名空间
-r /cmd_vel:=/vel     改话题名（模块 2 后面会用）
```

> 代码里写死的节点名只是**默认值**，CLI 可以覆盖。

---

## 四、实操步骤（手把手）

### 步骤 0 · 打开终端

Windows：打开 **Windows Terminal** → **Ubuntu**。

**预期**：出现 `<用户名>@<电脑名>:~$` 提示符。

### 步骤 1 · source 环境并确认包

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 pkg executables my_first_pkg
```

**预期**：

```text
my_first_pkg hello_node
```

### 步骤 2 · 跑起来，列出节点

终端 A：

```bash
ros2 run my_first_pkg hello_node
```

终端 B（新开）：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 node list
```

**预期**：终端 B 打印 `/hello_node`。

### 步骤 3 · 看节点详情

```bash
ros2 node info /hello_node
```

**预期**：列出节点的 Publishers / Subscribers / Service Servers / Service Clients / Action Servers 等（hello_node 都是空的，只有基本信息）。

### 步骤 4 · 改节点名（不改代码）

先 `Ctrl+C` 停掉终端 A 的节点，再：

```bash
ros2 run my_first_pkg hello_node --ros-args -r __node:=hello2
```

终端 B：

```bash
ros2 node list
```

**预期**：看到 `/hello2`，不再是 `/hello_node`。

### 步骤 5 · 加命名空间

停掉节点，再跑：

```bash
ros2 run my_first_pkg hello_node --ros-args -r __ns:=/robot1 -r __node:=hello
```

终端 B：

```bash
ros2 node list
```

**预期**：

```text
/robot1/hello
```

### 步骤 6 · 同时跑两个，对照

终端 A：`ros2 run my_first_pkg hello_node` 
终端 C：`ros2 run my_first_pkg hello_node --ros-args -r __ns:=/robot2`

**预期**：`ros2 node list` 同时看到 `/hello_node` 和 `/robot2/hello_node`，互不冲突。

---

## 五、关键 API / 命令详解

| 名称 | 作用 |
| ---- | ---- |
| `Node.__init__('node_name')` | 创建节点并注册默认节点名（rclpy 里就是 `super().__init__('...')`） |
| `ros2 node list` | 列出当前图中所有节点 |
| `ros2 node info /名` | 查看节点的话题/服务/动作连接 |
| `--ros-args -r __node:=新名` | 运行时改节点名 |
| `--ros-args -r __ns:=/空间` | 运行时加命名空间 |
| `--ros-args -r /旧话题:=/新话题` | 话题重映射（后面几集会用） |

代码侧（回忆模块 1）：

```python
class HelloNode(Node):
    def __init__(self):
        # 这里只是"默认节点名"，CLI 可覆盖
        super().__init__('hello_node')
```

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| 两个同名节点只剩一个 | 节点名冲突，后启动的会顶掉先启动的 | 用 `__node:=` / `__ns:=` 区分 |
| 以为"一个包 = 一个节点" | 包是安装单位，节点是运行单位 | 一个包可有多个 `entry_points` |
| 改了 `super().__init__('名字')` 没生效 | 已被 CLI `__node:=` 覆盖，或没重启进程 | 先查 `ros2 node list`，再重启 |
| `--ros-args` 写在包名前面 | 位置不对，ros2 解析失败 | 写在**可执行名后面**：`ros2 run 包 可执行 --ros-args ...` |
| `ros2 node list` 是空的 | 没 source，或节点已退出 | source 两层；确认节点还在跑 |

---

## 七、预期输出汇总

1. `ros2 node list` 能看到 `/hello_node`；
2. `--ros-args -r __node:=hello2` 后变成 `/hello2`；
3. 加 `__ns:=/robot1` 后变成 `/robot1/hello`；
4. 同一程序多开不冲突；
5. 能分清包名 / 可执行名 / 节点名。

---

## 八、小作业（5 分钟）

1. **不改代码**，让 hello 节点以名字 `/demo/my_hello` 运行。

   提示：

   ```bash
   ros2 run my_first_pkg hello_node --ros-args -r __ns:=/demo -r __node:=my_hello
   ```

   预期：`ros2 node list` 显示 `/demo/my_hello`。

2. 用 `ros2 node info /demo/my_hello` 确认它活着。

---

## 九、下集预告

节点之间怎么传数据？下集讲**话题与消息类型**：用 `ros2 topic echo / hz / pub` 观察一条速度指令在图上流动。
