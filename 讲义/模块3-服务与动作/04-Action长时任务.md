# 3.4 Action：长时任务

> 模块 3 第 4 集 
> 前置：已完成 3.3，Service 能跑通。

---

## 一、本集目标

理解 Action 的 **goal / feedback / result / cancel** 生命周期：

- 什么时候该用 Action（而不是 Service）；
- `.action` 三段式怎么读；
- 状态机：ACCEPTED → EXECUTING → SUCCEEDED / CANCELED / ABORTED。

---

## 二、效果演示

想象"前进 5 米"任务（下一集真跑）：

```text
客户端: 发送目标 前进 5.00 m
服务端: 目标已接受
服务端: 反馈进度: 10%
服务端: 反馈进度: 20%
...
服务端: 反馈进度: 100%
客户端: 结果: success=True, traveled=5.00 m
```

中途取消：

```text
客户端: 2.0s 后请求取消…
服务端: 已取消，已走 1.20 m
客户端: 结果: success=False, traveled=1.20 m
```

**预期**：你看到"有进度、能取消、有最终结果"——这正是 Action 的三件套。

---

## 三、理论讲解

### 3.1 比喻：点外卖

| 外卖环节 | Action 术语 |
| -------- | ----------- |
| 下单"一份牛肉面" | goal |
| App 显示"骑手已到店 / 正在配送" | feedback |
| 显示"已送达"或"已取消" | result |
| 路上点"取消订单" | cancel |

### 3.2 `.action` 三段式

```text
# goal：你想干什么
float32 distance
---
# result：最终结果
bool success
float32 distance_traveled
---
# feedback：过程进度
float32 progress
```

顺序固定：**goal → result → feedback**。

对应 `MoveDistance.action`（本系列自定义）：

| 段 | 字段 | 含义 |
| -- | ---- | ---- |
| goal | `distance` | 目标前进距离（米） |
| result | `success` / `distance_traveled` | 是否成功 / 实际走了多少 |
| feedback | `progress` | 0.0~1.0 进度 |

### 3.3 状态机

```text
        发送 goal
           │
           ▼
       ACCEPTED ───拒绝──▶ (结束)
           │
           ▼
      EXECUTING ──取消──▶ CANCELED
           │
           ├─正常完成──▶ SUCCEEDED
           └─出错────▶ ABORTED
```

| 状态 | 含义 | 谁触发 |
| ---- | ---- | ------ |
| ACCEPTED | 服务端接了这单 | `goal_callback` 返回 ACCEPT |
| EXECUTING | 正在跑 | `execute_callback` 开始 |
| SUCCEEDED | 成功到达 | `goal_handle.succeed()` |
| CANCELED | 中途取消 | `goal_handle.canceled()` |
| ABORTED | 出错中止 | `goal_handle.abort()` |

### 3.4 Action vs Service

| 维度 | Service | Action |
| ---- | ------- | ------ |
| 比喻 | 打电话 | 点外卖 |
| 执行时长 | 短（秒内） | 长（秒到分钟） |
| 过程反馈 | 无 | 有 feedback |
| 可取消 | 否 | 是 |
| 例子 | 查电量、开灯 | 导航、前进 N 米、抓取 |

**Action 不是"更快的 Service"**，它解决的是"长时 + 进度 + 取消"。

### 3.5 什么时候别用 Action

- 瞬时完成（开灯）→ Service；
- 纯数据流（激光）→ Topic；
- 只是要个参数值 → Parameter。

硬把短任务做成 Action，只是多写一堆回调，没有任何好处。

---

## 四、实操步骤（手把手）

本集以**读文件 + 画状态机**为主；代码实现放在下一集。

### 步骤 0 · 打开终端

Windows Terminal → Ubuntu。

**预期**：`<用户名>@<电脑名>:~$` 提示符。

### 步骤 1 · 看 MoveDistance.action

```bash
cat ~/ros2_ws/src/my_interfaces/action/MoveDistance.action
```

**预期**：三段，两条 `---`。

### 步骤 2 · 用 interface show 看生成结果

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 interface show my_interfaces/action/MoveDistance
```

**预期**：

```text
# goal
float32 distance
---
# result
bool success
float32 distance_traveled
---
# feedback
float32 progress
```

### 步骤 3 · 对照三件套填空

在纸上填：

| 问题 | 答案 |
| ---- | ---- |
| goal 是什么？ | `distance`：目标距离 |
| result 是什么？ | `success` + `distance_traveled` |
| feedback 是什么？ | `progress` 0~1 |

**预期**：三格都填上。

### 步骤 4 · 画状态机

画出：ACCEPTED → EXECUTING → SUCCEEDED / CANCELED，并标注"谁调用哪个方法"（下一集会用）。

**预期**：图上能看出"取消"是 EXECUTING 分出来的支路。

### 步骤 5 · 场景判断复习

| 任务 | Topic / Service / Action |
| ---- | ------------------------ |
| 持续发速度指令 | Topic |
| 查电量 | Service |
| 前进 5 米，可取消 | Action |
| 开灯 | Service |
| 导航到点（几分钟） | Action |
| 订阅激光 | Topic |

**预期**：至少对 5 / 6。

---

## 五、关键 API / 命令详解

本集 API 先"见名字"，下一集逐个实现：

| 名称 | 作用 |
| ---- | ---- |
| `ActionServer(self, Type, name, execute_callback, goal_callback, cancel_callback)` | 建动作服务端 |
| `ActionClient(self, Type, name)` | 建动作客户端 |
| `goal_handle.publish_feedback(feedback)` | 发一条进度 |
| `goal_handle.is_cancel_requested` | 有人请求取消了吗 |
| `goal_handle.canceled()` | 标记为已取消 |
| `goal_handle.succeed()` | 标记为成功 |
| `client.send_goal_async(goal, feedback_callback=...)` | 发送目标（异步） |
| `goal_handle.cancel_goal_async()` | 请求取消 |

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| 把无反馈短任务做成 Action | 误解 Action = 快 Service | 短任务用 Service |
| Action 与 Topic 混用没想清 | 同一数据既 pub 又 action | 数据流 Topic，任务 Action |
| 取消不生效 | `execute` 里不检查 `is_cancel_requested` | 循环里检查并 `canceled()` |
| 进度一直 0% 或 100% | feedback 没真正 `publish_feedback` | 见下一集代码 |
| goal 段字段写太多 | Action 的 goal 要精简 | 只放"任务目标"必要字段 |

---

## 七、预期输出汇总

1. 能背出 `.action` 三段：goal / result / feedback；
2. 能画出状态机：ACCEPTED → EXECUTING → SUCCEEDED/CANCELED/ABORTED；
3. 场景判断至少 5/6 正确；
4. 能说出 Action 与 Service 的分界线（长时 / 进度 / 取消）。

---

## 八、小作业（5 分钟）

写出下面三件事各用哪种通信，并一句话说明：

1. 导航到点；
2. 开灯；
3. 电量查询。

参考答案：Action（长时、要进度）；Service（瞬时、要确认）；Service（一问一答）。

---

## 九、下集预告

下集手写 **Action Server / Client**：`move_server` 模拟前进、发进度、支持取消；`move_client` 发目标、收反馈、演示 cancel。
