# 1.3 turtlesim 与 ros2 CLI

> 模块 1 第 3 集 
> 前置：已完成 1.2，`printenv ROS_DISTRO` 为 `jazzy`。

---

## 一、本集目标

会用 `ros2 run / node / topic / param` 核心命令**观察并控制** turtlesim 乌龟。

---

## 二、效果演示

三个终端同时工作：

| 终端 | 在干什么 |
| ---- | -------- |
| A | 跑着一只蓝色背景的小乌龟 |
| B | 键盘遥控，乌龟画圆 |
| C | `ros2 topic echo` 实时打印速度指令 |

**最终现象**：你按键盘 → 乌龟动 → 终端 C 能看到 `linear.x` 在变。

"发号施令"和"偷听指令"同时成立，这就是 ROS2 的日常。

---

## 三、理论讲解

### 3.1 turtlesim 是什么？

ROS2 自带的**教学小仿真**：一个窗口、一只乌龟、几个话题。

| 谁 | 干什么 | 角色 |
| -- | ------ | ---- |
| `turtlesim_node` | 显示乌龟、执行移动 | **订阅者**（听速度指令） |
| `turtle_teleop_key` | 把键盘按键变成速度指令 | **发布者**（广播速度） |

用 1.1 的比喻：teleop 是**广播电台**，turtlesim 是**收音机**，广播的内容是"速度"。

### 3.2 可执行 ≠ 节点名

| 层级 | 例子 | 含义 |
| ---- | ---- | ---- |
| **包名** | `turtlesim` | 软件包 |
| **可执行名** | `turtlesim_node`、`turtle_teleop_key` | `ros2 run` 后面那个词 |
| **节点名** | `/turtlesim`、`/teleop_turtle` | 运行后在图里的名字 |

命令格式：

```bash
ros2 run <包名> <可执行名>
```

### 3.3 话题：list / echo / hz / info

| 命令 | 作用 | 比喻 |
| ---- | ---- | ---- |
| `ros2 topic list` | 列出所有话题 | 看有哪些电台 |
| `ros2 topic echo <话题>` | 实时打印消息 | 调频收听 |
| `ros2 topic hz <话题>` | 测发布频率 | 测电台语速 |
| `ros2 topic info <话题>` | 看类型和节点 | 看电台节目表 |

乌龟速度指令的话题是 `/turtle1/cmd_vel`，消息类型是 `geometry_msgs/msg/Twist`。

### 3.4 参数

节点还有**旋钮**（Parameter）。turtlesim 有背景色、线宽等参数：

```bash
ros2 param list /turtlesim
```

### 3.5 多终端的习惯

ROS2 日常几乎永远开着 2–3 个终端：

- 有的终端**被节点占着**（teleop、echo）；
- 有的终端**用来敲命令**。

Windows Terminal 的多标签（`Ctrl+Shift+T`）或 VS Code 终端分栏都很方便。

---

## 四、实操步骤（手把手）

下面用 **终端 A / B / C** 区分。每个终端都先确认环境：

```bash
source /opt/ros/jazzy/setup.bash
```

（若已写入 `~/.bashrc` 可省略。）

### 步骤 0 · 打开三个终端

Windows Terminal → 打开三个 **Ubuntu** 标签（`Ctrl+Shift+T` 新建）。

**预期**：三个提示符 `<用户名>@<电脑名>:~$`。

### 步骤 1 · 终端 A：启动乌龟

```bash
ros2 run turtlesim turtlesim_node
```

> 工作目录：任意。

**预期**：弹出窗口"ROS turtlesim"，蓝色背景，中间一只小乌龟。

> 若 `turtlesim: No such package`：`sudo apt install -y ros-jazzy-turtlesim` 后重试。

### 步骤 2 · 终端 B：启动键盘遥控

```bash
ros2 run turtlesim turtle_teleop_key
```

**预期**：终端显示控制说明（方向键控制移动，`g|b|v|c|d|e|r|t`键旋转到指定方向，`f` 取消旋转）。**点一下这个终端**让它获得键盘焦点。

按一下方向键：

**预期**：乌龟窗口里小乌龟开始移动。

### 步骤 3 · 终端 C：看节点

```bash
ros2 node list
```

**预期**：至少两个节点，类似

```text
/teleop_turtle
/turtlesim
```

### 步骤 4 · 终端 C：看话题

```bash
ros2 topic list
```

**预期**：看到 `/turtle1/cmd_vel`、`/turtle1/color_sensor`、`/turtle1/pose`、`/parameter_events`、`/rosout` 等。

### 步骤 5 · 终端 C：偷听速度指令

```bash
ros2 topic echo /turtle1/cmd_vel
```

然后去**终端 B** 按 `↑` 持续前进。

**预期**：终端 C 不停打印类似

```text
linear:
  x: 2.0
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0
```

按 `Ctrl+C` 停止 echo。

### 步骤 6 · 终端 C：测频率与详情

```bash
ros2 topic hz /turtle1/cmd_vel
ros2 topic info /turtle1/cmd_vel
```

（`hz` 在你按着键时才会有稳定数字，看完 `Ctrl+C`。）

**预期**：

- `hz` 打印 `average rate: ...`（约十几 Hz，取决于按键）；
- `info` 显示 `Type: geometry_msgs/msg/Twist`，Publisher / Subscriber 计数。

### 步骤 7 · 终端 C：看参数

```bash
ros2 param list /turtlesim
```

**预期**：列出 `background_b/g/r`、`width` 等参数名。

### 步骤 8 · 收尾

两个 `Ctrl+C`：先停 teleop（终端 B），再停 turtlesim（终端 A）。

**预期**：乌龟窗口关闭，两个终端回到提示符。

---

## 五、关键 API / 命令详解

| 命令 | 作用 | 本集例子 |
| ---- | ---- | -------- |
| `ros2 run <包> <可执行>` | 运行包里的可执行 | `ros2 run turtlesim turtlesim_node` |
| `ros2 node list` | 列出运行中的节点 | 看到 `/turtlesim` |
| `ros2 topic list` | 列出话题 | `/turtle1/cmd_vel` |
| `ros2 topic echo <话题>` | 打印消息流 | 偷听速度 |
| `ros2 topic hz <话题>` | 测频率 | 按键时测 |
| `ros2 topic info <话题>` | 类型与连接信息 | `geometry_msgs/msg/Twist` |
| `ros2 param list <节点>` | 列参数 | `/turtlesim` 的旋钮 |
| `ros2 doctor` | 环境体检 | 出问题先跑 |

消息 `Twist` 常用字段：

| 字段 | 含义 |
| ---- | ---- |
| `linear.x` | 前后线速度（m/s，乌龟像素） |
| `angular.z` | 转弯角速度（rad/s） |

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| `Package 'turtlesim' not found` | 没装或没 source | `sudo apt install -y ros-jazzy-turtlesim`；`source /opt/ros/jazzy/setup.bash` |
| 敲了键盘乌龟不动 | teleop 终端没有键盘焦点 | **点一下** teleop 那个终端再按 |
| 终端被 teleop 占满，没法敲命令 | 只开了一个终端 | 多开终端（A/B/C） |
| `ros2 topic echo` 无输出 | 话题名写错 / 没人在发 | `ros2 topic list` 核对；按住 teleop 键 |
| 包名和可执行名搞混 | `ros2 run turtlesim turtlesim` | 包=`turtlesim`，可执行=`turtlesim_node` |
| `hz` 一直 `no new messages` | 没按键盘 | 按住方向键（如 `↑`）再看 |
| 关了窗口节点还在 | 进程没退干净 | 对应终端 `Ctrl+C` |
| 只抄命令说不出谁发谁收 | 没理解角色 | 记住：teleop=发布，turtlesim=订阅 |

---

## 七、预期输出汇总

1. 乌龟窗口出现并随键盘移动；
2. `ros2 node list` 至少 `/turtlesim` 与 `/teleop_turtle`；
3. `ros2 topic echo /turtle1/cmd_vel` 能打印 `linear.x`；
4. `ros2 topic info` 显示类型 `geometry_msgs/msg/Twist`；
5. `ros2 param list /turtlesim` 有参数列表。

---

## 八、小作业（5 分钟）

**不查笔记**，写出命令（并实际跑一遍验证）：

1. 查看 `/turtle1/cmd_vel` 的**消息类型**；
2. 查看 `/turtle1/cmd_vel` 的**发布频率**。

答案核对：`ros2 topic info /turtle1/cmd_vel` 与 `ros2 topic hz /turtle1/cmd_vel`。

---

## 九、下集预告

会用别人的节点了。下集**自己建包**：工作空间 `~/ros2_ws` 怎么摆、`ros2 pkg create` 一把生成 `my_first_pkg`。
