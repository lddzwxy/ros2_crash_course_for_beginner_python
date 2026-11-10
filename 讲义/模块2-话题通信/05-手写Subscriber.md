# 2.5 手写 Subscriber（Python 3.12）

> 模块 2 第 5 集 
> 前置：已完成 2.4，`my_topic_demo` 包已存在，`velocity_publisher` 可运行。

---

## 一、本集目标

订阅 `/cmd_vel` 并解析处理：

- 会写 `create_subscription`；
- 理解回调签名 `callback(msg)`；
- 知道**回调必须短小**，阻塞 = 丢消息；
- 跑通 pub + sub 双终端对照。

---

## 二、效果演示

终端 A：

```bash
ros2 run my_topic_demo velocity_publisher
```

终端 B：

```bash
ros2 run my_topic_demo velocity_subscriber
```

**预期**：终端 B 跟着 A 的节奏打印（每 20 条一条）：

```text
[INFO] [velocity_subscriber]: 开始订阅 /cmd_vel
[INFO] [velocity_subscriber]: [1] 收到: linear.x=0.15, angular.z=0.00
[INFO] [velocity_subscriber]: [21] 收到: linear.x=0.24, angular.z=0.09
[INFO] [velocity_subscriber]: [41] 收到: linear.x=0.25, angular.z=0.17
```

数值与 A 发出的对应。

---

## 三、理论讲解

### 3.1 订阅者 = 报名听广播

```text
publisher ──发──▶ /cmd_vel ──收──▶ subscriber
```

订阅者只要：

1. 说清楚**听哪个话题**、**什么类型**；
2. 交给 ROS2 一个**回调函数**；
3. 有消息来，回调自动被调用。

你不需要写循环去"轮询有没有新消息"。

### 3.2 回调签名

```python
def listener_callback(self, msg: Twist):
    ...
```

- 参数 `msg` 就是收到的完整消息对象；
- `msg.linear.x`、`msg.angular.z` 取字段；
- 回调运行在 `spin` 的事件循环里——**回调没返回，下一条消息就排着队**。

### 3.3 回调阻塞的危害（重点）

```python
# 危险示范：回调里睡 5 秒
def listener_callback(self, msg):
    time.sleep(5)   # 这 5 秒里新消息全在排队 / 被丢弃
    print(msg)
```

后果：

- 消息积压或丢失（QoS 队列有深度）；
- 同节点的其它回调也卡住；
- 频率越高，丢得越惨。

**铁律**：回调只做"取字段、简单判断、打日志/发命令"，重活丢到别的线程或下一拍。

### 3.4 队列深度 10 是什么

```python
self.create_subscription(Twist, topic_name, self.listener_callback, 10)
```

最后的 `10` 是 QoS 深度：最多缓存 10 条等你处理。处理不过来就丢旧的。深度细节见下一集 QoS。

---

## 四、实操步骤（手把手）

### 步骤 0 · 打开终端

Windows Terminal → Ubuntu。

**预期**：`<用户名>@<电脑名>:~$` 提示符。

### 步骤 1 · 确认已有包

```bash
cd ~/ros2_ws/src/my_topic_demo
ls my_topic_demo
```

**预期**：至少有 `velocity_publisher.py`、`__init__.py`。

### 步骤 2 · 写 velocity_subscriber.py

**设计动机**：

- 与 publisher 对称：同样参数化 `topic_name`；
- 回调短小：取字段、合法性检查、节流打印；
- 用 `count % 20` 控制日志量，避免 10 Hz 刷屏。

完整代码（与仓库 `code/src/my_topic_demo/my_topic_demo/velocity_subscriber.py` 一致）：

```python
#!/usr/bin/env python3
# 速度指令订阅者：订阅 /cmd_vel 并解析线速度/角速度
# 教学点：create_subscription、回调短小、日志分级

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class VelocitySubscriber(Node):
    """订阅速度指令，打印并做简单合法性检查。"""

    def __init__(self):
        super().__init__('velocity_subscriber')

        self.declare_parameter('topic_name', '/cmd_vel')
        topic_name = self.get_parameter('topic_name').value

        # 创建订阅者：类型、话题、回调、QoS 深度
        self.subscription = self.create_subscription(
            Twist, topic_name, self.listener_callback, 10)

        self.count = 0
        self.get_logger().info(f'开始订阅 {topic_name}')

    def listener_callback(self, msg: Twist):
        """收到一条速度指令就处理一次；回调要短小、不要阻塞。"""
        self.count += 1
        lin = msg.linear.x
        ang = msg.angular.z

        # 简单合法性检查：异常值用 warning
        if abs(lin) > 2.0 or abs(ang) > 2.0:
            self.get_logger().warning(
                f'速度偏大: linear.x={lin:.2f}, angular.z={ang:.2f}')

        # 每 20 条打印一次，避免刷屏
        if self.count % 20 == 1:
            self.get_logger().info(
                f'[{self.count}] 收到: linear.x={lin:.2f}, angular.z={ang:.2f}')


def main(args=None):
    rclpy.init(args=args)
    node = VelocitySubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

文件路径：

```text
~/ros2_ws/src/my_topic_demo/my_topic_demo/velocity_subscriber.py
```

**预期**：保存成功，PEP8 缩进 4 空格。

### 步骤 3 · 确认 setup.py 入口

`setup.py` 的 `entry_points` 应包含：

```python
entry_points={
    'console_scripts': [
        'velocity_publisher = my_topic_demo.velocity_publisher:main',
        'velocity_subscriber = my_topic_demo.velocity_subscriber:main',
    ],
},
```

**预期**：两行都在；`velocity_subscriber = my_topic_demo.velocity_subscriber:main` 三段一致。

### 步骤 4 · 编译

```bash
cd ~/ros2_ws
colcon build --symlink-install --packages-select my_topic_demo
```

**预期**：

```text
Starting >>> my_topic_demo
Finished <<< my_topic_demo [0.58s]
Summary: 1 package finished
```

### 步骤 5 · source 环境

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

**预期**：`ros2 pkg executables my_topic_demo` 有 `velocity_subscriber`。

### 步骤 6 · 双终端跑 pub + sub

终端 A：

```bash
ros2 run my_topic_demo velocity_publisher
```

终端 B（另开并 source）：

```bash
ros2 run my_topic_demo velocity_subscriber
```

**预期**：

- A：`开始发布速度到 /cmd_vel，频率 10.0 Hz`
- B：`开始订阅 /cmd_vel`，随后 `[1] 收到: ...`、`[21] 收到: ...`
- 数值与 A 的日志对应。

### 步骤 7 · 第三终端确认连接

```bash
ros2 topic info /cmd_vel
```

**预期**：

```text
Type: geometry_msgs/msg/Twist
Publisher count: 1
Subscription count: 1
```

### 步骤 8 · 手动注入一条异常速度

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 3.0}, angular: {z: 0.0}}"
```

**预期**：终端 B 出现 warning：

```text
[WARN] [velocity_subscriber]: 速度偏大: linear.x=3.00, angular.z=0.00
```

---

## 五、关键 API / 命令详解

| 名称 | 作用 |
| ---- | ---- |
| `create_subscription(Type, topic, callback, qos)` | 建订阅者 |
| `callback(msg)` | 收到消息时被调用；`msg` 为完整消息对象 |
| `msg.linear.x` / `msg.angular.z` | 取 Twist 字段 |
| `self.subscription` | 保存订阅句柄，防止被垃圾回收（必须赋值给成员） |
| `get_logger().warning(...)` | 黄色警告日志，适合异常值 |
| `ros2 topic info /cmd_vel` | 查看 pub/sub 数量，确认两端都连上 |

> **必须把订阅句柄存成成员**： `self.subscription = self.create_subscription(...)` 
> 写成局部变量可能被 Python 回收，订阅就悄悄失效。

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| 有话题、无数据 | pub/sub 有一方没跑；或 QoS 不兼容 | `ros2 topic info -v` 看端点；对齐 QoS（见 2.6） |
| 回调里 `time.sleep(5)` 后大量丢消息 | 回调阻塞，队列溢出 | 回调保持短小；重活异步做 |
| 日志刷屏看不清 | 10 Hz × 每条都打 | 节流：`count % 20 == 1` 才打 |
| 订阅"时灵时不灵" | 订阅句柄没存成员被回收 | `self.subscription = ...` |
| `ModuleNotFoundError` 或找不到可执行 | 忘 source 新 build 的 install | 每次 build 后 `source install/setup.bash` |
| 只有 sub 没有 pub | 以为订阅会凭空产生数据 | 先跑 publisher 或 `topic pub` 注入 |

---

## 七、预期输出汇总

1. 双终端运行，B 的日志频率与 A 一致（约 10 Hz 上报、20 条一打）；
2. `ros2 topic info /cmd_vel` 显示 `Publisher count: 1`、`Subscription count: 1`；
3. 手动 `pub` 一个 `linear.x=3.0`，B 打印 `速度偏大` warning；
4. `ros2 node list` 同时有 `/velocity_publisher` 与 `/velocity_subscriber`。

---

## 八、小作业（5 分钟）

1. 在回调里加一条规则：仅当 `linear.x > 0.5` 时打印 warning（把 0.25 的正常范围和 0.5 分开）；

   提示：

   ```python
   if lin > 0.5:
       self.get_logger().warning(f'前进偏快: {lin:.2f}')
   ```

2. 把 `topic_name` 参数改成 `/robot1/cmd_vel`，pub/sub 都用同一参数启动，确认仍能收到（`ros2 topic list` 出现 `/robot1/cmd_vel`）。

---

## 九、下集预告

为什么有时**连上了却收不到**？下集拆 QoS：Reliable / Best Effort、深度、兼容性规则，附"有话题无数据"排查清单。
