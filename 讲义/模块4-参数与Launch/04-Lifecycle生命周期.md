# 4.4 Lifecycle 生命周期（了解为主）

> 模块 4 第 4 集 
> 前置：已完成 4.3，会启动 `my_bringup` 多节点。本集**了解为主**，不深挖状态机细节。

---

## 一、本集目标

看懂 Lifecycle 四态与四条迁移，会手动：

`configure → activate → （观察发数据）→ deactivate` 。

能回答一个面试常问：为什么节点起来了却不发数据？

---

## 二、效果演示

终端 A：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run my_bringup lifecycle_demo
```

**预期**：只打印

```text
[INFO] [lifecycle_demo]: lifecycle_demo 创建（unconfigured）
```

**没有任何心跳**。别急，节点没坏——它在等你"开机"。

终端 B：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 lifecycle set /lifecycle_demo configure
ros2 lifecycle set /lifecycle_demo activate
```

**预期**：终端 A 依次出现

```text
[INFO] [lifecycle_demo]: 已 configure：publisher 就绪
[INFO] [lifecycle_demo]: 已 activate：开始发布
```

然后 `ros2 topic echo /lc_heartbeat` 能收到 `lc heartbeat`。

---

## 三、理论讲解

### 3.1 比喻：设备开机流程

普通节点 = 插电就转的电风扇。 
Lifecycle 节点 = **工业设备**：上电自检（configure）→ 使能（activate）→ 干活 → 停用（deactivate）→ 断电清理（cleanup）。

好处：硬件驱动、导航栈这种"重资源"节点，可以先占好资源、等人确认，再放数据。

### 3.2 四个状态

```text
unconfigured  ──configure──►  inactive  ──activate──►  active
     ▲                             │                          │
     │                          cleanup                   deactivate
     └───── cleanup ◄──────┴◄──────────────┘
                                    │
                                 finalize
                                    ▼
                               finalized
```

| 状态 | 含义 | 典型动作 |
| ---- | ---- | -------- |
| unconfigured | 刚创建，啥都没开 | 构造函数只做最小初始化 |
| inactive | 资源已开，不发数据 | `on_configure` 建 publisher |
| active | 正常干活 | `on_activate` 开定时器 |
| finalized | 彻底结束 | 不可再迁移 |

### 3.3 四条主要迁移

| 命令 | 迁移 | 回调 |
| ---- | ---- | ---- |
| `configure` | unconfigured → inactive | `on_configure` 开资源 |
| `activate` | inactive → active | `on_activate` 开定时器 |
| `deactivate` | active → inactive | `on_deactivate` 停定时器 |
| `cleanup` | inactive → unconfigured | `on_cleanup` 释放资源 |

**核心规则**：未 `activate`，lifecycle publisher **不发数据**（就算你调了 `publish`）。

### 3.4 什么时候需要？

- 硬件驱动：先配置串口/相机，再出数；
- 模式切换：暂停任务时 `deactivate`，恢复再 `activate`；
- 系统集成：导航栈等上层就绪后再激活传感器。

入门阶段：**见过、会敲命令、知道未 activate 不发数**，就够用。

---

## 四、实操步骤（手把手）

> 仓库对照：`code/src/my_bringup/my_bringup/lifecycle_demo.py`。 
> 可执行名：`lifecycle_demo`，节点名：`/lifecycle_demo`。

### 步骤 0 · 打开两个终端

两个终端都执行：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

**预期**：两边都能 `ros2 -h` 出帮助。

### 步骤 1 · 写 lifecycle_demo.py

**动机**：

- 继承 `rclpy.lifecycle.Node` 而不是普通 `Node`；
- `on_configure` 建 `create_lifecycle_publisher`，`on_activate` 才 `create_timer`；
- 迁移回调要返回 `super().on_xxx(state)`：基类会把迁移转发给托管实体（publisher），漏了它 `publish()` 会静默丢消息；
- 这样"没激活就一定没数据"在结构上成立。

```python
#!/usr/bin/env python3
# Lifecycle 演示节点（了解）：configure/activate 后才开始发布
# 教学点：生命周期状态机；未 activate 不发数据

import rclpy
from rclpy.lifecycle import Node as LifecycleNode, State, TransitionCallbackReturn
from std_msgs.msg import String


class LifecycleDemo(LifecycleNode):
    """最小 Lifecycle 节点：on_configure 开资源，on_activate 开定时器。"""

    def __init__(self):
        super().__init__('lifecycle_demo')
        self.publisher_ = None
        self.timer = None
        self.get_logger().info('lifecycle_demo 创建（unconfigured）')

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        self.publisher_ = self.create_lifecycle_publisher(String, '/lc_heartbeat', 10)
        self.get_logger().info('已 configure：publisher 就绪')
        # super() 会把迁移转发给托管实体（lifecycle publisher），必须调用
        return super().on_configure(state)

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        # 激活后才启动定时器
        self.timer = self.create_timer(1.0, self._on_timer)
        self.get_logger().info('已 activate：开始发布')
        # 必须调用 super()：它激活 lifecycle publisher，
        # 否则 publish() 会被 @when_enabled 拦下，消息静默丢弃
        return super().on_activate(state)

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        if self.timer:
            self.destroy_timer(self.timer)
            self.timer = None
        self.get_logger().info('已 deactivate：停止发布')
        return super().on_deactivate(state)

    def on_cleanup(self, state: State) -> TransitionCallbackReturn:
        if self.publisher_:
            self.destroy_publisher(self.publisher_)
            self.publisher_ = None
        self.get_logger().info('已 cleanup')
        return super().on_cleanup(state)

    def _on_timer(self):
        msg = String()
        msg.data = 'lc heartbeat'
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = LifecycleDemo()
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

确认 `setup.py` entry_points 有：

```python
'lifecycle_demo = my_bringup.lifecycle_demo:main',
```

**预期**：继承的是 `rclpy.lifecycle.Node`；回调里做完自己的事，**返回 `super().on_xxx(state)`**（转发给 lifecycle publisher 等托管实体）。

### 步骤 2 · 编译并启动

```bash
cd ~/ros2_ws
colcon build --packages-select my_bringup --symlink-install
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run my_bringup lifecycle_demo
```

**预期**：终端 A 只有一条"创建（unconfigured）"；**没有**心跳日志。

### 步骤 3 · 查看生命周期状态

终端 B：

```bash
ros2 lifecycle list /lifecycle_demo
```

**预期**：列出可用迁移，例如

```text
- configure [1]
        Start: unconfigured
        Goal: configuring
- shutdown [5]
        Start: unconfigured
        Goal: shuttingdown
```

再看当前状态：

```bash
ros2 lifecycle get /lifecycle_demo
```

**预期**：`unconfigured [1]`（或等价描述）。

### 步骤 4 · configure

```bash
ros2 lifecycle set /lifecycle_demo configure
```

**预期**：`Transitioning successful`；终端 A 打印"已 configure：publisher 就绪"。

此时**仍无数据**：

```bash
ros2 topic echo /lc_heartbeat
```

**预期**：卡住无输出（按 `Ctrl+C` 退出 echo）——publisher 在，但未激活不发。

### 步骤 5 · activate

```bash
ros2 lifecycle set /lifecycle_demo activate
```

**预期**：终端 A 打印"已 activate：开始发布"；`ros2 topic echo /lc_heartbeat` 每秒一条

```text
data: 'lc heartbeat'
```

### 步骤 6 · deactivate

```bash
ros2 lifecycle set /lifecycle_demo deactivate
```

**预期**：终端 A 打印"已 deactivate：停止发布"；echo 再次无新消息。

### 步骤 7 · cleanup（可选）

```bash
ros2 lifecycle set /lifecycle_demo cleanup
```

**预期**：打印"已 cleanup"；回到 unconfigured，可再次 configure。

---

## 五、关键 API / 命令详解

| 名称 | 作用 |
| ---- | ---- |
| `rclpy.lifecycle.Node` | Lifecycle 节点基类 |
| `create_lifecycle_publisher(...)` | 生命周期发布者，未 activate 不发 |
| `on_configure/on_activate/on_deactivate/on_cleanup` | 迁移回调，返回 `super().on_xxx(state)`（其基类实现返回 `SUCCESS/FAILURE/ERROR`） |
| `TransitionCallbackReturn.SUCCESS` | 迁移成功 |
| `ros2 lifecycle list <node>` | 列出可执行迁移 |
| `ros2 lifecycle get <node>` | 查看当前状态 |
| `ros2 lifecycle set <node> <transition>` | 触发迁移（configure/activate/…） |

状态口诀：**unconfigured → inactive → active →（可回退）→ finalized**。

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| 节点"没反应"、无数据 | 状态停在 unconfigured/inactive | `ros2 lifecycle set ... configure` 再 `activate` |
| `Invalid transition` | 当前状态不允许该迁移 | `ros2 lifecycle get` 看状态，按顺序迁移 |
| `Unknown node` | 节点名写错 / 没 source | 对照 `ros2 node list`，注意是 `/lifecycle_demo` |
| 用普通 `create_publisher` 打包进 Lifecycle | 未受生命周期管理 | 用 `create_lifecycle_publisher` |
| activate 后仍无数据（无报错） | 回调没调 `super().on_activate(state)`，publisher 未被激活，`publish()` 被静默拦下 | 迁移回调返回 `super().on_xxx(state)` |
| 回调忘了 `return ...` | 迁移显示失败 | 每个回调显式 `return super().on_xxx(state)` |

---

## 七、预期输出汇总

1. 启动后仅 unconfigured，无心跳；
2. `configure` 后 publisher 就绪，仍无数据；
3. `activate` 后 `/lc_heartbeat` 1 Hz 输出；
4. `deactivate` 后数据停止；
5. 能口述四条迁移：configure / activate / deactivate / cleanup。

---

## 八、小作业（5 分钟）

1. 只 `configure` 不 `activate`，用 `ros2 topic info /lc_heartbeat` 观察 Publisher 数量变化；
2. `deactivate` 后再 `activate`，确认数据恢复，不必重新 configure；
3. （想一想）如果 `on_activate` 里创建定时器失败，应该返回 `FAILURE` 还是 `ERROR`？

---

## 九、下集预告

功能都齐了。最后一集把工程收干净：**4.5 项目结构与代码规范**——依赖写进 package.xml、rosdep 一键装、README 让别人能复现。
