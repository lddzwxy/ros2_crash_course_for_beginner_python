# 5.1 RQT 工具箱

> 模块 5 第 1 集 
> 前置：模块 2–4 已有可跑的 pub/sub 与 `my_bringup` 多节点；图形界面可用（WSLg 或 Linux 桌面）。

---

## 一、本集目标

用 **rqt** 家族四件套看清系统：

`rqt_graph（拓扑）→ rqt_console（日志）→ rqt_plot（曲线）→ rqt_publisher（手动发消息）` 。

结束时你不再只会 `ros2 topic echo`，而是有一块"仪表盘"。

---

## 二、效果演示

终端 A 一键起小系统：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch my_bringup demo_system.launch.py
```

终端 B：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
rqt_graph
```

**预期**：弹出窗口，实时拓扑大致如下——

```text
[sim_sensor] ──/detection──► [decision_node] ──/cmd_vel──► [mock_driver]
[param_node] ──/heartbeat──► (孤立节点或悬空话题)
```

节点是椭圆，箭头是数据流。谁在跟谁说话，一眼看穿。

---

## 三、理论讲解

### 3.1 rqt 是什么？

rqt = ROS 的**仪表台**。一堆 Qt 插件，可以单独开，也可以 `rqt` 一个窗口里多标签。

| 工具 | 看什么 | 类比 |
| ---- | ------ | ---- |
| `rqt_graph` | 节点/话题拓扑 | 电路图 |
| `rqt_console` | 日志级别过滤 | 黑匣子 |
| `rqt_plot` | 数值随时间曲线 | 示波器 |
| `rqt_publisher` | 话题消息、手动 publish | 信号发生器 |

### 3.2 为什么要图，不直接命令行？

命令行适合精确查数；图适合**第一次看陌生系统**：

- 谁发布了 `/cmd_vel`？图上一指就有；
- 两个节点为什么没连上？图上缺边；
- 系统是不是在刷屏？console 高度一眼可见。

调试顺序建议：**先 graph 看结构 → 再 console 看异常 → 再 plot 看数值 → 最后 topic 手动试**。

### 3.3 WSLg 注意

Windows + WSL2 的 GUI 走 **WSLg**。若 `rqt` 报错或黑屏，先：

```bash
echo $DISPLAY
sudo apt install -y mesa-utils libgl1-mesa-dri
```

`DISPLAY` 一般非空即可。仍不行就重启 WSL（Windows 里 `wsl --shutdown`）。

### 3.4 插件从哪来

单独开：`rqt_graph` / `ros2 run rqt_console rqt_console` / `ros2 run rqt_plot rqt_plot` / `ros2 run rqt_publisher rqt_publisher`。 
或统一：`rqt` → 菜单 Plugins → 逐个加载。教学用单独命令，路径最短。

---

## 四、实操步骤（手把手）

### 步骤 0 · 打开终端并确认图形环境

Windows Terminal → Ubuntu：

```bash
echo $DISPLAY
rqt_graph --help
```

**预期**：`DISPLAY` 类似 `:0`；`rqt_graph` 能打印帮助（不报 command not found）。

若找不到命令：

```bash
sudo apt update
sudo apt install -y ros-jazzy-rqt-graph ros-jazzy-rqt-console ros-jazzy-rqt-plot ros-jazzy-rqt-topic ros-jazzy-rqt-publisher
```

### 步骤 1 · 启动被观察的系统

终端 A（整栈）：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch my_bringup demo_system.launch.py
```

**预期**：节点日志在刷。

### 步骤 2 · rqt_graph 看拓扑

终端 B：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
rqt_graph
```

**预期**：窗口出现，能看到 `sim_sensor → decision_node → mock_driver` 链路。

操作：工具栏切换 **Nodes only** / **Topics**；点上方刷新按钮，启动新节点后拓扑会更新。

### 步骤 3 · rqt_console 看日志

终端 B：

```bash
ros2 run rqt_console rqt_console
```

**预期**：日志表格出现，列有 Message / Severity / Node / Stamp。

操作：

1. 顶部 Severity 过滤器只勾 **Warn + Error**；
2. 观察：障碍过近时出现

```text
Warn  decision_node  障碍过近 (0.xx m)，停车
```

3. 全勾恢复，看 Info 流。

### 步骤 4 · rqt_plot 画数值

先确认有可画的数值话题。`/cmd_vel` 是 Twist：

```bash
ros2 run rqt_plot rqt_plot /cmd_vel/linear/x
```

**预期**：曲线窗口出现，`linear.x` 在 0.0 与 0.2 之间阶跃（决策在停/走）。

若用 `my_topic_demo` 的 velocity_publisher，会看到正弦曲线更漂亮：

```bash
ros2 run rqt_plot rqt_plot /cmd_vel/linear/x /cmd_vel/angular/z
```

**预期**：两条平滑波动曲线。

### 步骤 5 · rqt_publisher 手动发消息

```bash
ros2 run rqt_publisher rqt_publisher
```

**预期**：左侧话题列表出现。

操作：

1. 选中 `/cmd_vel`；
2. 类型选 `geometry_msgs/msg/Twist`；
3. 设置发布频率；
4. 展开 `linear.x` 设为 0.5，
5. 勾选 Enable 即可周期发布；
6. 回终端看 `mock_driver` 是否打印"执行: linear.x=0.50"。

**预期**：mock_driver 日志跟上你的手动指令——**你不改代码也能注入信号**。

### 步骤 6 · 用 graph 回答问题：谁在发 /cmd_vel？

在 `rqt_graph` 里点 `/cmd_vel` 话题框。

**预期**：边高亮，上游是 `decision_node`（若同时开了 velocity_publisher，会看到两个上游——这正是多主冲突的可视化）。

---

## 五、关键 API / 命令详解

| 名称 | 作用 |
| ---- | ---- |
| `rqt_graph` | 实时节点/话题拓扑 |
| `rqt_console` | 日志查看器，按级别/节点过滤 |
| `rqt_plot <topic/field>` | 画数值字段随时间变化 |
| `rqt_topic` / `rqt_publisher` | 查看话题消息 / 手动构造并周期发布消息 |
| `rqt` | 插件容器，多工具合一 |
| Severity 过滤 | 只看 Warn/Error，从噪声里捞异常 |
| Publish 面板 | 人工注入消息，验证订阅端 |

字段写法：`/cmd_vel/linear/x` = 话题 / 消息字段路径。

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| `qt.qpa.plugin: could not load display` / 黑屏 | WSLg/DISPLAY 未就绪 | `echo $DISPLAY`；装 mesa；重启 WSL |
| `rqt_graph` 是空的 | 没 source / 节点没起 | 两层 source；先 `ros2 node list` |
| 图上有节点但没边 | 话题名不一致或没 pub/sub 配对 | `ros2 topic info` 查；点话题框看连接 |
| `rqt_plot` 没曲线 | 绑错字段 / 话题无数值类型 | 用 `/cmd_vel/linear/x` 这类字段路径 |
| console 里啥也没有 | 日志级别被过滤掉 | 重置过滤器，勾上 Info |
| 只看 graph 不看 console | 错过异常 | 养成 graph → console 顺序 |
| rqt 打开很慢 | 首次加载插件 | 等几秒；后续会快 |

---

## 七、预期输出汇总

1. `rqt_graph` 显示 `sim_sensor → decision_node → mock_driver`；
2. `rqt_console` 过滤出"障碍过近"WARN；
3. `rqt_plot` 看到 `linear.x` 阶跃或正弦曲线；
4. `rqt_publisher` 手动发 Twist，`mock_driver` 有响应。

---

## 八、小作业（5 分钟）

1. 用 `rqt_graph` 找出当前系统**谁在发 `/cmd_vel`**（把名字写下来）；
2. 在 `rqt_console` 里只留 Error，确认正常运行时应该**是空的**；
3. 用 `rqt_publisher` 往 `/detection` 手动发 `data: distance=0.1`，观察 decision_node 是否立刻停车并打 WARN。

---

## 九、下集预告

现场看懂了，怎么把现场**存下来、再回放**？下一集 **5.2 ros2 bag 录放**。
