# 2.6 QoS 与 Topic 坑合集

> 模块 2 第 6 集 
> 前置：已完成 2.4 / 2.5，pub + sub 能跑通。

---

## 一、本集目标

会排查"**有话题、无数据**"，理解：

- Reliability：Reliable vs Best Effort；
- Durability：Volatile vs Transient Local；
- History / Depth；
- 兼容性规则（为什么有的组合收不到）；
- 入门默认策略：**Reliable + Volatile**。

---

## 二、效果演示

故意让两端 QoS 不兼容：

```text
Publisher  → Best Effort
Subscriber → Reliable
```

结果：话题在、节点在、`topic info` 看得到两端，**echo 却永远空白**。

对齐成同一 Reliability 后，数据立刻恢复。

**预期**：你意识到"断网/没跑"是错觉，真凶是 **QoS 不兼容**。

---

## 三、理论讲解

### 3.1 QoS 是什么

QoS = Quality of Service（服务质量），是发布/订阅之间的"投递协议"：

| 维度 | 通俗说法 | 取值 |
| ---- | -------- | ---- |
| Reliability | 要不要保证送到 | `reliable`（必达，重传） / `best_effort`（尽量，丢了算了） |
| Durability | 晚来的人能不能拿到旧数据 | `volatile`（不存） / `transient_local`（存一份，新人来了发） |
| History / Depth | 队列留几条 | `keep_last: N` / `keep_all` |

### 3.2 两种 Reliability 用在哪

| 场景 | 选什么 | 为什么 |
| ---- | ------ | ------ |
| 速度指令 `/cmd_vel` | Reliable | 丢一条车会顿挫 |
| 激光 / 图像流 | Best Effort | 丢一帧下一帧马上来，重传反而卡 |
| 状态 / 地图 | Reliable + Transient Local | 后启动的节点要立刻看到最新状态 |

### 3.3 兼容性规则（重点）

发布端 Offered 与订阅端 Requested 必须满足：

```text
Requested Reliable   → Offered 必须是 Reliable
Requested Best Effort → Offered 可以是 Best Effort 或 Reliable
```

一句话：**订户要求"必达"，发方必须承诺必达；订户接受"尽力"，发方怎样都行。**

| 发布 / 订阅 | Reliable | Best Effort |
| ----------- | -------- | ----------- |
| Reliable | ✅ | ✅ |
| Best Effort | ❌ 无数据 | ✅ |

所以：**Best Effort 发布 + Reliable 订阅 = 收不到任何东西**。

### 3.4 Depth 是什么

Depth = 队列最多缓存几条。

- `depth=1`：只留最新，中间的全丢；
- `depth=10`：缓冲 10 条，处理不过来丢旧的。

速度指令 `depth=10` 足够；地图只要最新一张，`depth=1` 即可。

### 3.5 入门默认策略

CONTRACT 建议：

| 场景 | Reliability | Durability | Depth |
| ---- | ----------- | ---------- | ----- |
| 命令/控制 | Reliable | Volatile | 10 |
| 传感器流 | Best Effort | Volatile | 5 |
| 状态/地图 | Reliable | Transient Local | 1 |

**学习阶段：统一默认（Reliable + Volatile + depth 10），先跑通再调。**

---

## 四、实操步骤（手把手）

### 步骤 0 · 打开终端

Windows Terminal → Ubuntu。

**预期**：`<用户名>@<电脑名>:~$` 提示符。

### 步骤 1 · 启动 pub + sub 基线

终端 A：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run my_topic_demo velocity_publisher
```

终端 B：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run my_topic_demo velocity_subscriber
```

**预期**：B 正常收到 `[1] 收到: ...`。

### 步骤 2 · 看端点 QoS

终端 C：

```bash
ros2 topic info /cmd_vel -v
```

**预期**：出现两段 `Publisher` / `Subscription`，每段含类似：

```text
QoS profile:
  Reliability: RMW_QOS_POLICY_RELIABILITY_RELIABLE
  Durability: RMW_QOS_POLICY_DURABILITY_VOLATILE
  ...
  Depth: 10
```

记下两端的 Reliability。

### 步骤 3 · 判断"在不在发"

```bash
ros2 topic hz /cmd_vel
ros2 node list
ros2 node info /velocity_publisher
```

**预期**：

- `hz` 约 10 Hz；
- `node list` 两个节点都在；
- `node info` 显示 publisher 的 Publications 含 `/cmd_vel`。

### 步骤 4 · 制造 QoS 不兼容（演示）

把**订阅端**改成要求 Reliable，**发布端**改成 Best Effort（用 CLI 覆盖不了 QoS 时，在代码里临时改，或用 `ros2 topic pub` 指定 QoS）。

最快复现方式——用 CLI 的 `--qos-reliability`：

```bash
# 终端 A：Best Effort 发布（用 topic pub 模拟）
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.2}}" --qos-reliability best_effort -r 10
```

```bash
# 在终端 B，强制 echo 使用 reliable
ros2 topic echo /cmd_vel --qos-reliability reliable
```

**预期**：`echo` **没有任何数据**；但：

```bash
ros2 topic info /cmd_vel -v
```

两端都在、类型正确——典型的"QoS 不兼容"。

### 步骤 5 · 对齐后恢复

把 echo 也改成 Best Effort：

```bash
ros2 topic echo /cmd_vel --qos-reliability best_effort
```

**预期**：立刻开始打印消息。

### 步骤 6 · 整理排查清单

按下面五步走一遍（对照你刚才的现象）：

```text
1. 节点在不在？     ros2 node list
2. 话题在不在？     ros2 topic list
3. 有没有数据？     ros2 topic hz / echo
4. 类型对不对？     ros2 topic info + ros2 interface show
5. QoS 兼不兼容？   ros2 topic info -v
```

**预期**：能把"有话题无数据"定位到第 5 步。

---

## 五、关键 API / 命令详解

| 名称 | 作用 |
| ---- | ---- |
| `ros2 topic info <话题> -v` | 显示端点与 QoS profile（排障利器） |
| `ros2 topic hz <话题>` | 判断是否在发、发多快 |
| `ros2 node info <节点>` | 确认 pub/sub 关系 |
| `ros2 topic echo --qos-reliability best_effort` | 临时改 echo 的 QoS |
| `ros2 topic pub --qos-reliability best_effort` | 临时改 pub 的 QoS |

代码侧显式 QoS（进阶，了解即可）：

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy

qos = QoSProfile(depth=5, reliability=ReliabilityPolicy.BEST_EFFORT)
self.publisher_ = self.create_publisher(Twist, topic_name, qos)
```

入门阶段**先别改代码 QoS**，默认传 `10` 就是 Reliable + Volatile + depth 10。

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| 话题在、节点在、echo 却无数据 | Best Effort 发布 + Reliable 订阅 | 对齐 Reliability（见步骤 5） |
| 传感器数据时断时续 | 订阅端 Reliable 重传挤爆队列 | 传感器用 Best Effort |
| 只收到最新一条，中间全丢 | Depth=1 | 控制类调到 10 |
| 后启动的节点看不到状态 | Volatile，不存历史 | 状态话题用 Transient Local |
| 以为 Topic"断了" | 其实是 QoS 不兼容 | 先跑 `topic info -v` |
| 换 rmw 实现后行为不同 | 不同 rmw 对 QoS 细节支持有差异 | 入门统一默认 QoS，不折腾 |

---

## 七、预期输出汇总

1. `ros2 topic info /cmd_vel -v` 能读出 Reliability / Durability / Depth；
2. 能复现"Best Effort 发 + Reliable 订 = 无数据"；
3. 对齐 QoS 后数据恢复；
4. 背下 5 步排查清单：节点 → 话题 → 数据 → 类型 → QoS；
5. 知道入门默认：Reliable + Volatile + depth 10。

---

## 八、小作业（5 分钟）

1. 制造一次 QoS 不匹配（按步骤 4），把 `ros2 topic info /cmd_vel -v` 的输出抄进笔记；
2. 按 5 步清单排障并恢复，记下"哪一步发现问题"。

---

## 九、下集预告

模块 2 收工。下集进入**模块 3**：一问一答的 **Service**——从 turtlesim 的 `/spawn` 开始，感受"打电话"式通信。
