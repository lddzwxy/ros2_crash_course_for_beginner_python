# 模块 2 · 话题通信 Topic（细纲 · 6 集）

> 目标：理解并手写发布/订阅，跑通 `/cmd_vel` 速度指令通信。 
> 前置：模块 1 已有 `my_first_pkg`，会 colcon 闭环。 
> 产出包：`my_topic_demo`（ament_python，扩展自 my_first_pkg 风格）。 
> 契约：`/cmd_vel` · `geometry_msgs/msg/Twist`（系列契约，后续不改名）。

---

## 2.1 通信总览：Topic / Service / Action

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 建立三种通信方式的直觉，会做"用哪种"的初步判断 |
| 开场演示 | 同一张对比表 + 生活比喻动画：广播 / 打电话 / 点外卖 |
| 知识点 | ① Topic=单向连续广播（传感器、速度指令）② Service=一问一答（查询、开关）③ Action=可反馈可取消的长时任务（导航、抓取）④ 列表：频率高、要确认、要进度 |
| 跟做步骤 | 无终端实操；完成决策练习题（3 个场景选通信方式） |
| 常见坑 | 用 Service 传高频传感器数据（会把系统卡死）；把 Action 当成"更快的 Service" |
| 预期输出 | 能说出：速度指令用 Topic、查电量用 Service、导航到点用 Action |
| 小作业 | 写出你手机上 3 个像 Topic / Service / Action 的例子 |
| 下集预告 | 先深入 Topic 的载体：节点 |

---

## 2.2 节点 Node

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 理解节点=可执行进程里的"工作单位"，会改名、加命名空间、remap |
| 开场演示 | 同一可执行跑两次，节点名/命名空间不同，`ros2 node list` 对照 |
| 知识点 | ① 节点职责单一 ② 节点名 vs 可执行名 vs 包名 ③ 命名空间 `/ns/node` ④ `ros2 run ... --ros-args -r __node:=xx -r __ns:=yy` ⑤ 一个包可有多个可执行 |
| 跟做步骤 | **1** `ros2 run my_first_pkg hello_node`<br>**2** `ros2 node list` / `ros2 node info /hello_node`<br>**3** 重映射名：`ros2 run my_first_pkg hello_node --ros-args -r __node:=hello2`<br>**4** 加命名空间：`--ros-args -r __ns:=/robot1`<br>**5** 观察 `ros2 node list` 变化 |
| 关键命令 | `ros2 node list/info`、`--ros-args -r __node:=` / `__ns:=` |
| 常见坑 | 以为"一个包 = 一个节点"；节点名写死在代码里导致多开冲突（用 remap 或让 rclpy 用 CLI 名） |
| 预期输出 | 同一程序在不同 ns 下显示为 `/robot1/hello2` |
| 小作业 | 不改代码，让 hello 节点以名字 `/demo/my_hello` 运行 |
| 下集预告 | 节点之间怎么传数据？话题与消息类型 |

---

## 2.3 话题与消息类型

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 看懂 msg 字段，会用 `topic info/echo/hz/type` |
| 开场演示 | turtlesim 下 `ros2 topic echo /turtle1/cmd_vel` 配键盘控制 |
| 知识点 | ① 话题名 + 类型 ② `geometry_msgs/Twist` 字段 linear/angular ③ 常用包 std_msgs / geometry_msgs / sensor_msgs / nav_msgs ④ `interface show` |
| 跟做步骤 | **1** `ros2 topic list -t`<br>**2** `ros2 topic info /turtle1/cmd_vel`<br>**3** `ros2 interface show geometry_msgs/msg/Twist`<br>**4** `ros2 topic echo /turtle1/cmd_vel`<br>**5** `ros2 topic hz /turtle1/cmd_vel`<br>**6** `ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}}"` |
| 关键命令 | `ros2 topic list/info/echo/hz/pub`、`ros2 interface show` |
| 常见坑 | 类型不匹配导致没数据/连不上；`pub` 的 YAML 缩进写错 |
| 预期输出 | 能读懂 Twist 的 x/z 含义；pub 后乌龟动一下 |
| 小作业 | 查出 `/turtle1/pose` 的类型，并 echo 一条 |
| 下集预告 | 自己写 Publisher 发 `/cmd_vel` |

---

## 2.4 手写 Publisher（Python 3.12）

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 手写定时发布 `Twist` 到 `/cmd_vel`，理解 timer 与 spin |
| 开场演示 | 运行 velocity_publisher，`ros2 topic echo /cmd_vel` 看到速度在变 |
| 知识点 | ① `create_publisher` ② `create_timer` ③ 回调里 publish ④ `rclpy.spin` ⑤ 为什么不用 sleep 循环而用 timer |
| 跟做步骤 | **1** `cd ~/ros2_ws/src && mkdir -p my_topic_demo`（或 `ros2 pkg create`）<br>**2** 写 `velocity_publisher.py`：类继承 Node，`super().__init__('velocity_publisher')`，declare 频率参数，默认 topic `/cmd_vel`，timer 回调里发线速度+微小角速度，日志打印<br>**3** 配 `package.xml`（依赖 rclpy、geometry_msgs）、`setup.py` entry_points、`setup.cfg`、`resource/`<br>**4** `cd ~/ros2_ws && colcon build --symlink-install --packages-select my_topic_demo`<br>**5** `source install/setup.bash`<br>**6** `ros2 run my_topic_demo velocity_publisher`<br>**7** 另一终端 `ros2 topic echo /cmd_vel` 与 `ros2 topic hz /cmd_vel` |
| 关键 API | `self.create_publisher(Twist, '/cmd_vel', 10)`、`self.create_timer(0.1, self.timer_cb)`、`self.get_logger().info(...)`、`rclpy.spin(node)` |
| 常见坑 | ① 只调了 publish 没 spin（收不到）② 消息类型 import 写错 `geometry_msgs.msg.Twist` ③ 频率参数未 declare 就 get |
| 预期输出 | echo 中 linear.x 周期性变化；hz 约等于设定频率 |
| 小作业 | 把角速度改成正弦摆动，看到"左右画弧" |
| 下集预告 | 有喊话的了，下集写接听的 Subscriber |

---

## 2.5 手写 Subscriber（Python 3.12）

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 订阅 `/cmd_vel` 并处理回调；理解回调短小、避免阻塞 |
| 开场演示 | pub + sub 同开，sub 日志随 pub 变化 |
| 知识点 | ① `create_subscription` ② 回调签名 `msg` ③ QoS 队列深度 ④ 回调阻塞的危害 |
| 跟做步骤 | **1** 在 `my_topic_demo` 写 `velocity_subscriber.py`<br>**2** `create_subscription(Twist, '/cmd_vel', self.cb, 10)`<br>**3** 回调里解析 linear.x / angular.z 并 get_logger 打印（注意 throttle 或计数，避免刷屏）<br>**4** entry_points 增加 `velocity_subscriber`<br>**5** `colcon build --symlink-install --packages-select my_topic_demo` 并 source<br>**6** 两终端分别 run publisher / subscriber<br>**7** （可选）第三终端 `ros2 topic pub` 手动注入 |
| 关键 API | `create_subscription(Twist, topic, callback, qos_profile)` |
| 常见坑 | ① 回调里 `time.sleep(5)` 导致丢消息 ② QoS 与 pub 不兼容无数据 ③ 忘 source 新 build |
| 预期输出 | sub 日志频率与 pub 一致；数值对应 |
| 小作业 | 在 sub 中只在 `linear.x > 0.5` 时打印警告 |
| 下集预告 | 为什么有时连上了却收不到？QoS 与坑合集 |

---

## 2.6 QoS 与 Topic 坑合集

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 会排查"有话题无数据"，理解 reliable/best_effort、深度、兼容性 |
| 开场演示 | 故意让 pub best_effort、sub reliable → 无数据；再对齐后恢复 |
| 知识点 | ① Reliability：Reliable vs Best Effort ② Durability：Volatile vs Transient Local ③ History/Depth ④ 兼容性规则 ⑤ 入门策略：默认 Reliable+Volatile |
| 跟做步骤 | **1** `ros2 topic info /cmd_vel -v`（看端点 QoS）<br>**2** `ros2 topic hz` 判断是否在发<br>**3** `ros2 node info` 确认 pub/sub 关系<br>**4** （演示）在代码或 CLI 中改 QoS，制造不兼容并恢复<br>**5** 整理"有话题无数据"检查清单 |
| 关键命令 | `ros2 topic info -v`、`ros2 topic hz`、`ros2 node info` |
| 常见坑 | 传感器 Best Effort 与 Reliable 订阅混用；Depth=1 丢中间消息；以为 Topic 断了其实是 QoS |
| 预期输出 | 学员能独立完成 5 步排查：节点在不在 → 话题在不在 → 有没有数据 → 类型对不对 → QoS 兼不兼容 |
| 小作业 | 制造一次 QoS 不匹配并按清单恢复，截图/笔记记报错 |
| 下集预告 | 进入模块 3：一问一答的 Service |

---

## 本模块代码演进

| 集 | 对 `code/` 的改动 |
| -- | ----------------- |
| 2.4 | 新建 `src/my_topic_demo/`，`velocity_publisher.py` |
| 2.5 | 增加 `velocity_subscriber.py`，更新 entry_points |
| 2.6 | 可选：在 pub/sub 加 QoS 说明注释或小 demo |

> 配套讲义：`讲义/模块2-话题通信/01–06`。 
> 配套代码：`code/src/my_topic_demo/`。
