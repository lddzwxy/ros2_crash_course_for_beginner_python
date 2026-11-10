# 3.1 Service：一问一答

>  模块 3 第 1 集 
>  前置：模块 2 已熟练 Topic；会 `colcon build` + `source` 闭环。

---

## 一、本集目标

理解 Service 的**请求/响应**模型，会调用现成 Service：

```text
ros2 service list / type / call
ros2 interface show
```

并能说清"什么时候用 Service，什么时候用 Topic"。

---

## 二、效果演示

```bash
ros2 run turtlesim turtlesim_node
# 另起一个终端
ros2 service call /spawn turtlesim/srv/Spawn "{x: 2.0, y: 2.0, theta: 0.0, name: 'turtle2'}"
```

**预期**：小窗里**多出一只 turtle2**；终端打印：

```text
response:
turtlesim.srv.Spawn_Response(name='turtle2')
```

再换画笔颜色：

```bash
ros2 service call /turtle1/set_pen turtlesim/srv/SetPen "{r: 255, g: 0, b: 0, width: 3}"
ros2 run turtlesim turtle_teleop_key
```

**预期**：之后乌龟移动留下**红色轨迹**。

---

## 三、理论讲解

### 3.1 比喻：打电话

```text
你（Client）──"喂，开一下灯"──▶ 对方（Service）
你 ◀──"开了"────────────────── 对方
```

- 有明确的**问**（request）和**答**（response）；
- 一次通话结束，下次再打；
- 打通前对方得先"开机"（server 必须在线）。

对比 Topic 广播：广播不问你听没听，也不等你回话。

### 3.2 `.srv` 文件结构

```text
# request（请求）
字段1
字段2
---
# response（响应）
字段3
字段4
```

一条横线 `---` 把请求和响应分开。

例子（turtlesim 的 Spawn）：

```text
float32 x
float32 y
float32 theta
string name
---
string name
```

### 3.3 同步调用会阻塞

客户端发完 request 后要**等** response：

- 等待期间，客户端这条线不能干别的；
- server 处理慢，客户端就一直等。

所以 Service 适合**低频、短时、要结果**的请求：

| 适合 Service | 不适合 Service |
| ------------ | -------------- |
| 查询电量 | 10 Hz 激光数据 |
| 设置模式 | 速度指令 |
| 开灯 / 关灯 | 连续轨迹 |
| 清屏 / 生成模型 | 需要进度条的任务 |

### 3.4 与 Topic 对比

| 维度 | Topic | Service |
| ---- | ----- | ------- |
| 比喻 | 广播 | 打电话 |
| 方向 | 单向 | 请求 → 响应 |
| 有无确认 | 无 | 有（response） |
| 频率 | 高 | 低 |
| 阻塞 | 否 | 是（客户端等响应） |
| 例子 | `/cmd_vel` | `/spawn`、`/set_mode` |

---

## 四、实操步骤（手把手）

### 步骤 0 · 打开终端

Windows Terminal → Ubuntu。

**预期**：`<用户名>@<电脑名>:~$` 提示符。

### 步骤 1 · 启动 turtlesim

```bash
source /opt/ros/jazzy/setup.bash
ros2 run turtlesim turtlesim_node
```

**预期**：蓝色小窗 + 一只乌龟。

### 步骤 2 · 列出服务

另开终端（记得 source）：

```bash
ros2 service list
```

**预期**：至少看到：

```text
/clear
/kill
/reset
/spawn
/turtle1/set_pen
/turtle1/teleport_absolute
/turtle1/teleport_relative
/turtlesim/describe_parameters
...
```

### 步骤 3 · 查看服务类型

```bash
ros2 service type /spawn
```

**预期**：

```text
turtlesim/srv/Spawn
```

### 步骤 4 · 查看 srv 定义

```bash
ros2 interface show turtlesim/srv/Spawn
```

**预期**：

```text
float32 x
float32 y
float32 theta
string name
---
string name
```

上半段 request，下半段 response。

### 步骤 5 · 调用 /spawn 生成第二只乌龟

```bash
ros2 service call /spawn turtlesim/srv/Spawn "{x: 2.0, y: 2.0, theta: 0.0, name: 'turtle2'}"
```

**预期**：

- 小窗多出 turtle2；
- 终端打印 response，`name: 'turtle2'`。

### 步骤 6 · 改画笔颜色

```bash
ros2 service call /turtle1/set_pen turtlesim/srv/SetPen "{r: 255, g: 0, b: 0, width: 3}"
```

**预期**：之后 turtle1 画出**红色粗线**（用 teleop 或 `topic pub` 让它动一下）。

### 步骤 7 · 对照 Topic 与 Service

```bash
ros2 topic list
ros2 service list
```

**预期**：两个列表**不混在一起**；`/turtle1/cmd_vel` 在 topic 侧，`/spawn` 在 service 侧。

---

## 五、关键 API / 命令详解

| 名称 | 作用 |
| ---- | ---- |
| `ros2 service list` | 列出所有服务 |
| `ros2 service type <服务名>` | 查看服务接口类型 |
| `ros2 service call <服务名> <类型> <YAML>` | 手动发一次请求 |
| `ros2 interface show <包/srv/名>` | 查看 request/response 字段 |
| `ros2 interface list` | 列出所有可用接口 |

call 的 YAML 要按 **request 字段**填：

```bash
# SetPen 的 request: r, g, b, width, off
ros2 service call /turtle1/set_pen turtlesim/srv/SetPen \
  "{r: 255, g: 0, b: 0, width: 3, off: 0}"
```

字段名打错会报参数校验错误；类型不匹配同理。

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| `Service ... not found` | 服务端没启动 / 没 source | 先跑 server；source 两层 |
| `Failed to fetch service` | YAML 字段写错 | 对照 `interface show` 字段名 |
| 用 Service 传高频传感器 | 阻塞一问一答扛不住 | 换 Topic |
| 在节点回调里同步 `call` 另一个 Service | 回调阻塞，可能死锁 | 见 3.3 的 `call_async` |
| 把 Action 当"更快的 Service" | 概念混淆 | 长时/要进度/要取消才用 Action |
| 以为 Service 能广播给多个客户端 | Service 是一对一 | 要多播用 Topic |

---

## 七、预期输出汇总

1. `ros2 service list` 能找到 `/spawn`、`/turtle1/set_pen`；
2. `ros2 interface show turtlesim/srv/Spawn` 看懂 request/response；
3. `service call /spawn` 后多出 turtle2；
4. `service call /turtle1/set_pen` 后画笔变红；
5. 能说出 Topic vs Service 的区别。

---

## 八、小作业（5 分钟）

1. 调用 `/clear` 清屏，并观察小窗变化：

   ```bash
   ros2 service call /clear std_srvs/srv/Empty
   ```

2. 写出 `turtlesim/srv/Spawn` 的 request 字段（4 个）与 response 字段（1 个）。

---

## 九、下集预告

系统自带的接口不够用怎么办？下集**自定义 .msg / .srv / .action**：建 `my_interfaces` 接口包，生成自己的消息类型。
