# 4.1 参数 Parameter

> 模块 4 第 1 集 
> 前置：模块 2–3 已完成，会写 pub/sub 节点；工作空间 `~/ros2_ws` 可正常 `colcon build`。
> 本集开始新建包 `my_bringup`。仓库对照：`code/src/my_bringup/`。 

---

## 一、本集目标

给节点加上"可调旋钮"——**参数（Parameter）**，完成：

`声明参数 → 运行读取 → ros2 param set 动态改 → YAML 备份/加载` 闭环。

结束时你能回答：为什么频率不该写死在代码里？

---

## 二、效果演示

终端 A 启动参数演示节点：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run my_bringup param_node
```

**预期**：约 10 Hz 刷屏

```text
[INFO] [param_node]: param_node 已启动，可用 ros2 param set 修改频率
[INFO] [param_node]: heartbeat @ 10.00 Hz   （每 0.1 秒一条）
```

终端 B 改频率：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 param set /param_node publish_frequency 2.0
```

**预期**：终端 A 立刻变成约 2 Hz，并打印

```text
[INFO] [param_node]: 检测到频率变更: 10.0 -> 2.0
```

**不用重启节点、不用改代码**——这就是参数的威力。

---

## 三、理论讲解

### 3.1 参数是什么？

生活比喻：参数是电器上的**旋钮**。

- 代码 = 电机怎么转（写死的逻辑）
- 参数 = 转速旋钮（运行时可调）

"发布频率""话题名""停车阈值"这类数字，写死在 `.py` 里改一次要重编译；做成参数，现场一条命令就能调。

### 3.2 参数的三步曲

| 步骤 | 作用 | 类比 |
| ---- | ---- | ---- |
| `declare_parameter` | 声明：我有这个旋钮，默认值多少 | 出厂时贴旋钮标签 |
| `get_parameter` | 读取：现在旋钮拧到哪了 | 看一眼刻度 |
| `ros2 param set` / 回调 | 修改：拧旋钮 | 现场调节 |

**Jazzy 严格模式**：没 `declare` 就 `get`，直接报错。先声明再使用，没有例外。

### 3.3 参数类型

| 类型 | Python 侧 | 例子 |
| ---- | --------- | ---- |
| bool | `True` / `False` | `enable_debug` |
| int | `10` | `queue_size` |
| double | `10.0` | `publish_frequency` |
| string | `'/cmd_vel'` | `topic_name` |
| 数组 | `[1.0, 2.0]` | 白名单 |

注意：`10` 是 int，`10.0` 是 double。YAML 里写 `10` 会当 int，类型对不上可能被拒。

### 3.4 YAML：参数的"配置档案"

```yaml
# config/params.yaml
param_node:
  ros__parameters:
    publish_frequency: 5.0
    topic_name: /heartbeat
```

结构口诀：**节点名 → `ros__parameters` → 参数名: 值**。

节点名必须和代码里 `super().__init__('param_node')` 的名字**一字不差**，否则 YAML 不生效（静默失败，最阴险）。

### 3.5 只读 vs 可动态改

本集先做到"get 到最新值并生效"。工业上还有 `add_on_set_parameters_callback` 做校验/拦截，了解即可，不深挖。

---

## 四、实操步骤（手把手）

> 本集开始新建包 `my_bringup`。仓库对照：`code/src/my_bringup/`。 

### 步骤 0 · 打开终端

Windows：打开 **Windows Terminal**，下拉选 **Ubuntu**（或 `Ctrl+Shift+T` 新建 Ubuntu 标签）。

**预期**：出现 `<用户名>@<电脑名>:~$` 提示符。

### 步骤 1 · 创建包骨架

```bash
cd ~/ros2_ws/src
ros2 pkg create my_bringup --build-type ament_python --node-name param_node
```

**预期**：`find my_bringup -type f | sort` 至少看到 3 个占位文件。

### 步骤 2 · 写 param_node.py

**为什么这么写（动机）**：

- 参数在构造函数里 `declare`，一次声明全局可用；
- `get_parameter(...).value` 拿到 Python 原生类型；
- 用 `add_on_set_parameters_callback` 监听参数变更，`ros2 param set` 一改就能感知；
- 频率变化时**重建 timer**（`create_timer` 的周期在创建时固定）——重建动作放在参数回调里，不要在定时器回调里销毁自己。

完整代码（与 `code/src/my_bringup/my_bringup/param_node.py` 一致）：

```python
#!/usr/bin/env python3
# 参数演示节点：声明/读取参数，支持 ros2 param set 动态改频率
# 教学点：declare_parameter、参数变更回调、create_timer

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult
from std_msgs.msg import String


class ParamNode(Node):
    """按参数频率发布心跳字符串。"""

    def __init__(self):
        super().__init__('param_node')

        # 声明参数：名称、默认值、描述（可选）
        self.declare_parameter('publish_frequency', 10.0)
        self.declare_parameter('topic_name', '/heartbeat')

        self._frequency = self.get_parameter('publish_frequency').value
        self.publisher_ = self.create_publisher(
            String, self.get_parameter('topic_name').value, 10)
        self._rebuild_timer()

        # 参数变更回调：ros2 param set 会先进这里，可安全地重建定时器
        self.add_on_set_parameters_callback(self._on_params_set)

        self.get_logger().info('param_node 已启动，可用 ros2 param set 修改频率')

    def _rebuild_timer(self):
        """按当前频率重建定时器。

        注意：不要在定时器回调里销毁/重建自己所在的定时器（危险操作），
        所以重建动作统一放到参数回调里触发。
        """
        period = 1.0 / max(self._frequency, 0.1)
        if hasattr(self, 'timer'):
            self.destroy_timer(self.timer)
        self.timer = self.create_timer(period, self.timer_callback)

    def _on_params_set(self, params):
        """参数生效前的回调：感知频率变更并重建定时器。"""
        for p in params:
            if p.name == 'publish_frequency':
                new_freq = float(p.value)
                if abs(new_freq - self._frequency) > 1e-6:
                    self.get_logger().info(
                        f'检测到频率变更: {self._frequency} -> {new_freq}')
                    self._frequency = new_freq
                    self._rebuild_timer()
        return SetParametersResult(successful=True)

    def timer_callback(self):
        msg = String()
        msg.data = f'heartbeat @ {self._frequency:.2f} Hz'
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ParamNode()
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

**预期**：保存无语法红线；`python3 -m py_compile` 无输出。

### 步骤 3 · 配置 setup.py / setup.cfg / package.xml

`package.xml` 关键依赖（完整见仓库）：

```xml
<!-- ~/ros2_ws/src/my_bringup/package.xml 片段 -->
<depend>rclpy</depend>
<depend>std_msgs</depend>
<depend>geometry_msgs</depend>
<depend>launch</depend>
<depend>launch_ros</depend>
```

`setup.py` 的 `entry_points` 必须和文件名/函数名对齐：

```python
# ~/ros2_ws/src/my_bringup/setup.py 片段
entry_points={
    'console_scripts': [
        'param_node = my_bringup.param_node:main',
    ],
},
```

`setup.cfg`：

```ini
# ~/ros2_ws/src/my_bringup/setup.cfg
[develop]
script_dir=$base/lib/my_bringup
[install]
install_scripts=$base/lib/my_bringup
```

**预期**：三段字符串 `param_node` / `my_bringup.param_node` / `main` 与实际路径一致。

### 步骤 4 · 编译并 source

```bash
cd ~/ros2_ws
colcon build --packages-select my_bringup --symlink-install
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

**预期**：`Summary: 1 package finished`；`ros2 pkg executables my_bringup` 列出 `param_node`。

### 步骤 5 · 运行并列出参数

终端 A：

```bash
ros2 run my_bringup param_node
```

终端 B：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 param list /param_node
```

**预期**：

```text
/param_node:
  publish_frequency
  start_type_description_service
  topic_name
  use_sim_time
```

（`use_sim_time` 和 `start_type_description_service` 是系统自带，忽略即可。）

### 步骤 6 · 读取单个参数

```bash
ros2 param get /param_node publish_frequency
```

**预期**：`Double value is: 10.0`

### 步骤 7 · 动态修改频率

```bash
ros2 param set /param_node publish_frequency 2.0
```

**预期**：返回 `Set parameter successful`；终端 A 心跳明显变慢，并打印 `检测到频率变更: 10.0 -> 2.0`。

### 步骤 8 · dump 参数到 YAML

```bash
mkdir -p ~/ros2_ws/src/my_bringup/config
ros2 param dump /param_node > ~/ros2_ws/src/my_bringup/config/param_node.yaml
```

**预期**：`config/` 下出现类似 `param_node.yaml` 的文件，内容含 `ros__parameters`。

### 步骤 9 · 手写正式 params.yaml

`dump` 的文件可以当起点，但教学统一用下面这份（与仓库 `code/src/my_bringup/config/params.yaml` 一致）：

```yaml
# ~/ros2_ws/src/my_bringup/config/params.yaml
# my_bringup 参数：节点名与参数对齐
param_node:
  ros__parameters:
    publish_frequency: 5.0
    topic_name: /heartbeat

sim_sensor:
  ros__parameters:
    publish_frequency: 5.0
    min_distance: 0.2

decision_node:
  ros__parameters:
    stop_distance: 0.5
```

**预期**：缩进 2 空格；节点名与 `super().__init__(...)` 一致；`publish_frequency` 是 `5.0` 带小数点（double）。

### 步骤 10 · 用 YAML 启动（预告 launch 用法）

先用命令行参数验证 YAML 内容：

```bash
ros2 run my_bringup param_node --ros-args --params-file 
~/ros2_ws/src/my_bringup/config/params.yaml
# 另起一终端
ros2 param get /param_node publish_frequency
```

**预期**：心跳约 **5 Hz**（不再是默认 10 Hz），说明 YAML 已覆盖默认值。`Ctrl+C` 退出。

---

## 五、关键 API / 命令详解

| 名称 | 作用 |
| ---- | ---- |
| `declare_parameter(name, default)` | 声明参数并给默认值；Jazzy 未声明不可 get |
| `get_parameter(name).value` | 读取当前值，返回 Python 原生类型 |
| `add_on_set_parameters_callback(cb)` | 参数生效前的回调：感知变更、校验或重建资源 |
| `self.create_timer(period, cb)` | 按固定周期触发回调；改周期需销毁重建 |
| `self.destroy_timer(t)` | 销毁定时器（改频率时用） |
| `ros2 param list <node>` | 列出某节点全部参数 |
| `ros2 param get <node> <name>` | 读取参数当前值 |
| `ros2 param set <node> <name> <v>` | 运行时改参数 |
| `ros2 param dump <node>` | 把参数导出成 YAML |
| `--ros-args --params-file f.yaml` | 启动时从 YAML 加载参数 |

YAML 结构（必背）：

```text
<节点名>:
  ros__parameters:
    <参数名>: <值>
```

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| `Parameter 'xxx' not declared` | 没 declare 就 get/set | 构造函数里先 `declare_parameter` |
| `Set parameter failed` / 类型不符 | YAML 写 `10` 当 int，代码期望 double | 写成 `10.0` |
| YAML 加载了但值没变 | YAML 里节点名和实际节点名不一致 | 对照 `ros2 node list` 改 YAML 顶层键 |
| `Executable 'param_node' not found` | entry_points 写错或没重编译 | 核对 setup.py，`colcon build` |
| set 成功但行为没变 | 代码只在启动时读了一次 | 在回调里再 `get_parameter`（见 param_node） |
| 中文日志乱码 | 终端编码非 UTF-8 | `export LANG=zh_CN.UTF-8` 或换 Windows Terminal |

---

## 七、预期输出汇总

1. `ros2 param list /param_node` 看到 `publish_frequency`、`topic_name`；
2. `ros2 param get` 返回默认值；
3. `ros2 param set ... 2.0` 后心跳变慢，日志提示频率变更；
4. `ros2 param dump` 生成 YAML；
5. `--params-file` 加载后心跳约 5 Hz。

---

## 八、小作业（5 分钟）

1. 用 `ros2 param set /param_node topic_name /my_heartbeat` 试一试：话题名会变吗？（提示：publisher 只在构造时创建，set 后需重启才生效——想一想为什么。）
2. 给 `param_node` 增加一个 `message_prefix`（string）参数，心跳内容变成 `prefix + 频率`，set 后立即生效；
3. 用 `ros2 param dump` 再导出一次，对比手写 YAML 的差异。

---

## 九、下集预告

参数会了，怎么**一条命令**起一堆节点、还把 YAML 自动带上？进入 **4.2 Launch 一键多节点**。
