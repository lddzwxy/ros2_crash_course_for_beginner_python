# 5.2 ros2 bag 录放

> 模块 5 第 2 集 
> 前置：已有会发数据的节点（`my_topic_demo` 或 `my_bringup`）；会用 `ros2 topic echo`。

---

## 一、本集目标

用 **ros2 bag** 把话题数据"录下来、放回去"：

`ros2 bag record → info → play --rate` 闭环。

结束时你能在节点关掉后，依然用录的数据复现现场。

---

## 二、效果演示

终端 A 发数据：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run my_topic_demo velocity_publisher
```

终端 B 录 10 秒：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 bag record -o my_cmd_vel_bag /cmd_vel
```

（等约 10 秒，`Ctrl+C` 停止录制。）

关掉终端 A 的发布者，再放：

```bash
ros2 bag play my_cmd_vel_bag
```

另开终端 C：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 topic echo /cmd_vel
```

**预期**：发布者已死，但 echo **照样有数据**——bag 在"代打"现场。

---

## 三、理论讲解

### 3.1 bag 是什么？

比喻：话题数据的**行车记录仪**。

- `record`：把指定话题的每条消息写进文件夹；
- `play`：按时间轴把消息再发出来；
- `info`：查录像带里有什么、多少条。

包名是 **rosbag2**，命令行是 `ros2 bag`（**不是** ROS1 的 `rosbag`）。

### 3.2 为什么要录？

| 场景 | bag 的用法 |
| ---- | ---------- |
| 现场出 bug，回公司复现 | 录下出错时的话题，慢慢调试 |
| 同事没硬件 | 给他一个 bag，play 就有数据 |
| 回归测试 | 用"正常基线 bag"对比新版本输出 |
| 调参对比 | 同一段数据，换参数重放看效果 |

### 3.3 录什么、存哪

- 只录需要的话题，别全量录（图像/激光很占盘）；
- `-o my_bag` 指定输出**目录名**（默认带时间戳）；
- 目录里是 `mcap`（或 `.db3`）数据文件 + `metadata.yaml` 元数据，**整个目录**一起拷贝/压缩。

### 3.4 play 可以控速

```bash
ros2 bag play my_bag --rate 2    # 2 倍速
ros2 bag play my_bag --rate 0.5  # 半速，看细节
```

还有 `--loop` 循环、`--topics` 只放部分话题——调试利器。

---

## 四、实操步骤（手把手）

### 步骤 0 · 打开三个终端

每个都：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

**预期**：三边 `ros2 -h` 正常。

### 步骤 1 · 启动发布者（终端 A）

```bash
ros2 run my_topic_demo velocity_publisher
```

（或 `ros2 run my_bringup sim_sensor` 发 `/detection`。）

**预期**：日志显示正在发布。

### 步骤 2 · 确认有数据（终端 B）

```bash
ros2 topic list
ros2 topic hz /cmd_vel
```

**预期**：`/cmd_vel` 在列；`hz` 约等于参数频率（默认 10 Hz）。

### 步骤 3 · 录制（终端 B）

```bash
cd ~
ros2 bag record -o my_cmd_vel_bag /cmd_vel
```

**预期**：

```text
[INFO] [rosbag2_recorder]: Listening for topics...
[INFO] [rosbag2_recorder]: Subscribed to topic '/cmd_vel'
```

观察约 10 秒，按 `Ctrl+C` 停止。

**预期**：`Ctrl+C` 后提示已关闭；`ls ~/my_cmd_vel_bag` 看到数据文件（如 `my_cmd_vel_bag_0.mcap` + `metadata.yaml`）。

### 步骤 4 · 查看 bag 信息

```bash
ros2 bag info ~/my_cmd_vel_bag
```

**预期**：类似

```text
Files:             my_cmd_vel_bag_0.mcap
Bag size:          xxx KiB
Storage id:        mcap
ROS Distro:        jazzy
Duration:          12.500003032s
Start:             ...
End:               ...
Messages:          126
Topic information: Topic: /cmd_vel | Type: geometry_msgs/msg/Twist | Count: 126 | Serialization Format: cdr
```

**Messages > 0** 是硬指标。

### 步骤 5 · 停掉发布者，用 bag 回放

终端 A 的 `velocity_publisher` 按 `Ctrl+C` 退出。

终端 B：

```bash
ros2 bag play ~/my_cmd_vel_bag
```

**预期**：进度条式输出，结束后退出。

终端 C：

```bash
ros2 topic echo /cmd_vel
```

**预期**：play 期间能收到 Twist（linear.x 正弦变化）。

### 步骤 6 · 调速回放

```bash
ros2 bag play ~/my_cmd_vel_bag --rate 2
ros2 topic hz /cmd_vel    # 另开终端，对比频率
```

**预期**：`--rate 2` 时 `hz` 约为原来的 2 倍。

### 步骤 7 · （可选）录多话题

```bash
ros2 bag record -o my_multi_bag /cmd_vel /detection
ros2 bag info ~/my_multi_bag
```

**预期**：Topic information 列出两个话题及各自条数。

---

## 五、关键 API / 命令详解

| 名称 | 作用 |
| ---- | ---- |
| `ros2 bag record -o <dir> <topics...>` | 录制指定话题 |
| `ros2 bag record -a` | 录全部话题（慎用，占盘） |
| `ros2 bag info <dir>` | 查看条数、时长、话题类型 |
| `ros2 bag play <dir>` | 按时间轴回放 |
| `ros2 bag play <dir> --rate N` | N 倍速回放 |
| `ros2 bag play <dir> --loop` | 循环回放 |
| `ros2 bag play <dir> --topics ...` | 只回放部分话题 |
| `ros2 bag --help` | 查看全部子命令（convert 等） |

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| `rosbag: command not found` | 敲成了 ROS1 命令 | 用 `ros2 bag` |
| `No messages` / Count: 0 | 录制时话题没数据 / 名字错 | 先 `ros2 topic hz` 确认，再录 |
| 找不到 bag | 路径或工作目录不对 | `ros2 bag info ~/my_cmd_vel_bag` 用绝对路径 |
| 录了一堆无关话题，文件巨大 | 用了 `-a` 或挂了 `/camera` | 只列需要的话题名 |
| play 了但 echo 没数据 | 回放时话题名被改 / 没 source | `ros2 topic list` 看是否出现 |
| `Package 'rosbag2' not found` | 没装/没 source | `sudo apt install ros-jazzy-ros2bag` 后 source |
| 拷贝 bag 丢文件 | 只拷了 mcap 没拷 metadata.yaml | **整个目录**一起打包 |

---

## 七、预期输出汇总

1. `ros2 bag record` 显示 `Subscribed to topic '/cmd_vel'`；
2. `ros2 bag info` 的 Messages > 0，类型 `geometry_msgs/msg/Twist`；
3. 关掉发布者后 `ros2 bag play`，`ros2 topic echo /cmd_vel` 仍有数据；
4. `--rate 2` 时发布频率明显加快。

---

## 八、小作业（5 分钟）

1. 录 `/cmd_vel` + `/detection` 各约 5 秒，`ros2 bag info` 对照两条的 Count；
2. `ros2 bag play my_bag --rate 0.5`，用 `ros2 topic hz` 验证变慢；
3. 把 bag 目录 `tar`/`zip` 压缩，解压后 `info` 仍可读——记住：**目录要整包**。

---

## 九、下集预告

现场能存能放了。日志怎么写才有用？下一集 **5.3 日志与可观测性**——告别 `print`，用级别和上下文让 bug 自己浮出来。
