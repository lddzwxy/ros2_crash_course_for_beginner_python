# 3.5 Action Server / Client

> 模块 3 第 5 集
> 前置：已完成 3.4，理解 goal/feedback/result/cancel。
> 本集开始新建包 `my_action_demo`，仓库对照：`code/src/my_action_demo/`。 

## 一、本集目标

实现"前进 N 米"Action：

- `ActionServer`：goal 校验、execute、feedback、取消处理；
- `ActionClient`：`send_goal`、收 feedback、演示 cancel；
- 跑通进度打印 + 中途取消。

---

## 二、效果演示

终端 A：

```bash
ros2 run my_action_demo move_server
```

终端 B：

```bash
ros2 run my_action_demo move_client 5.0
```

**预期**：

```text
# 终端 A
[INFO] [move_action_server]: Action 服务 /move_distance 已就绪
[INFO] [move_action_server]: 开始前进 5.00 m
[INFO] [move_action_server]: 进度 20%，已走 1.00 m
...
[INFO] [move_action_server]: 到达目标，共 5.00 m

# 终端 B
[INFO] [move_action_client]: 发送目标: 前进 5.00 m
[INFO] [move_action_client]: 目标已接受
[INFO] [move_action_client]: 反馈进度: 10%
...
[INFO] [move_action_client]: 反馈进度: 100%
[INFO] [move_action_client]: 结果: success=True, traveled=5.00 m
```

中途取消（2 秒后自动 cancel）：

```bash
ros2 run my_action_demo move_client 5.0 2.0
```

**预期**：约 2 秒后打印 `已取消，已走 X.XX m`，客户端 `success=False`。

---

## 三、理论讲解

### 3.1 服务端三个回调

| 回调 | 干什么 | 返回 |
| ---- | ------ | ---- |
| `goal_callback` | 要不要接这单 | `GoalResponse.ACCEPT` / `REJECT` |
| `cancel_callback` | 收不收取消请求 | `CancelResponse.ACCEPT` / `REJECT` |
| `execute_callback` | 真正干活（长时） | 填 `Result` 并 `return` |

### 3.2 execute 里的循环铁律

```python
while traveled < goal.distance:
    if goal_handle.is_cancel_requested:   # ① 每圈检查取消
        goal_handle.canceled()
        ...
        return result
    traveled = min(traveled + step, goal.distance)  # 封顶，避免踩过终点
    goal_handle.publish_feedback(feedback)  # ② 发进度
    time.sleep(0.1)                        # ③ 模拟耗时
```

三件事缺一不可：

1. 检查取消（否则取消按钮永远无效）；
2. 发 feedback（否则客户端进度条不动）；
3. 真实耗时（否则瞬间完成，看不到过程）。

### 3.3 客户端流程

```text
wait_for_server → send_goal_async → 等接受 → get_result_async
                ↘ feedback_callback（边跑边打）
```

取消用 `goal_handle.cancel_goal_async()`（发"请求"，真停由 server 决定）。

### 3.4 为什么 client 里用 threading.Timer

client 主线程要 `spin_until_future_complete` 等结果，没法自己"等 2 秒再取消"。

用 `threading.Timer(2.0, cancel_fn)` 在另一个线程 2 秒后调 `cancel_goal_async`，主线程继续等结果。

---

## 四、实操步骤（手把手）

> 本集开始新建包 `my_action_demo`，仓库对照：`code/src/my_action_demo/`。 

### 步骤 0 · 打开终端

Windows Terminal → Ubuntu。

**预期**：`<用户名>@<电脑名>:~$` 提示符。

### 步骤 1 · 确认接口包

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 interface show my_interfaces/action/MoveDistance
```

**预期**：三段字段都在。没有就先回 3.2 build + source。

### 步骤 2 · 创建包

```bash
cd ~/ros2_ws/src
ros2 pkg create my_action_demo --build-type ament_python --dependencies rclpy my_interfaces --node-name move_server
```

**预期**：目录就绪。

### 步骤 3 · 写 move_server.py

**设计动机**：

- `speed_mps` 参数化模拟速度（可调，默认 0.2 m/s）；
- `goal_callback` 拒绝 `distance <= 0`；
- execute 循环累加里程、发 feedback、查取消。

完整代码（与仓库 `code/src/my_action_demo/my_action_demo/move_server.py` 一致）：

```python
#!/usr/bin/env python3
# Action 服务端：模拟"前进 N 米"，带进度反馈，支持取消
# 教学点：ActionServer、execute 回调、publish_feedback、取消处理

import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.executors import MultiThreadedExecutor, ExternalShutdownException

from my_interfaces.action import MoveDistance


class MoveActionServer(Node):
    """按速度参数模拟里程累加，达成目标距离后返回结果。"""

    def __init__(self):
        super().__init__('move_action_server')

        self.declare_parameter('speed_mps', 0.2)
        self.speed = self.get_parameter('speed_mps').value
        # 校验 speed，避免 step=0 导致死循环
        if self.speed <= 0.0:
            self.get_logger().error(
                f'speed_mps={self.speed} 非法（必须 > 0），回退为 0.2')
            self.speed = 0.2

        self._action_server = ActionServer(
            self,
            MoveDistance,
            '/move_distance',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
        )
        self.get_logger().info(
            f'Action 服务 /move_distance 已就绪（speed={self.speed} m/s）')

    def goal_callback(self, goal_request):
        """拒绝非正距离的目标。"""
        if goal_request.distance <= 0.0:
            self.get_logger().warning('拒绝目标：distance 必须 > 0')
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """接受取消请求（真正停止在 execute 里处理）。"""
        self.get_logger().info('收到取消请求')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        """执行逻辑：循环累加里程，发反馈，支持取消。"""
        goal = goal_handle.request
        feedback = MoveDistance.Feedback()
        result = MoveDistance.Result()

        traveled = 0.0
        step = self.speed * 0.1     # 每步前进的距离
        step_count = 0              # 用步数计数控制日志频率，避免浮点比较

        self.get_logger().info(f'开始前进 {goal.distance:.2f} m')

        while traveled < goal.distance:
            # 取消处理：必须在循环里检查
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result.success = False
                result.distance_traveled = traveled
                self.get_logger().info(f'已取消，已走 {traveled:.2f} m')
                return result

            # 限制 traveled 不超过目标，避免最后一步"踩过终点"
            traveled = min(traveled + step, goal.distance)
            feedback.progress = min(traveled / goal.distance, 1.0)
            goal_handle.publish_feedback(feedback)

            # 每 10 步（=1 秒）打印一次，语义与注释一致
            step_count += 1
            if step_count % 10 == 0:
                self.get_logger().info(
                    f'进度 {feedback.progress*100:.0f}%，已走 {traveled:.2f} m')

            time.sleep(0.1)

        goal_handle.succeed()
        result.success = True
        result.distance_traveled = traveled
        self.get_logger().info(f'到达目标，共 {traveled:.2f} m')
        return result


def main(args=None):
    rclpy.init(args=args)
    node = MoveActionServer()

    # ★ 关键：多线程执行器，保证 cancel service 不被 execute 阻塞
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

路径：`~/ros2_ws/src/my_action_demo/my_action_demo/move_server.py`

**预期**：`ActionServer` 五个关键参数（self、类型、名字、execute、goal/cancel 回调）都在。

### 步骤 4 · 写 move_client.py

完整代码（与仓库一致）：

```python
#!/usr/bin/env python3
# Action 客户端：发送前进目标、收反馈，示例中途取消
# 教学点：ActionClient、send_goal、feedback_callback、cancel_goal

import sys
import threading                                   

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.executors import ExternalShutdownException  
from rclpy.utilities import remove_ros_args

from my_interfaces.action import MoveDistance


class MoveActionClient(Node):
    """发送 /move_distance 目标并打印进度。"""

    def __init__(self):
        super().__init__('move_action_client')
        self._action_client = ActionClient(self, MoveDistance, '/move_distance')
        self._cancel_timer = None        # 保存引用以便退出前 cancel

    def send_goal(self, distance: float, cancel_after: float = 0.0):
        """发送 goal；cancel_after>0 表示 N 秒后取消。"""
        self._action_client.wait_for_server()

        goal_msg = MoveDistance.Goal()
        goal_msg.distance = float(distance)

        self.get_logger().info(f'发送目标: 前进 {distance:.2f} m')

        send_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback)
        rclpy.spin_until_future_complete(self, send_future)
        goal_handle = send_future.result()

        if not goal_handle.accepted:
            self.get_logger().error('目标被拒绝')
            return

        self.get_logger().info('目标已接受')
        result_future = goal_handle.get_result_async()

        # 定时取消（示例演示 cancel 路径）
        if cancel_after > 0:
            def _cancel():
                # 双重保险：进程已 shutdown 时绝不再碰 rclpy 对象
                if not rclpy.ok():
                    return
                self.get_logger().warning(f'{cancel_after}s 后请求取消…')
                cancel_future = goal_handle.cancel_goal_async()
                # 打印 cancel 结果
                cancel_future.add_done_callback(self._on_cancel_done)

            self._cancel_timer = threading.Timer(cancel_after, _cancel)
            self._cancel_timer.daemon = True     # 不阻塞进程退出
            self._cancel_timer.start()

        rclpy.spin_until_future_complete(self, result_future)
        result = result_future.result().result
        self.get_logger().info(
            f'结果: success={result.success}, traveled={result.distance_traveled:.2f} m')

        # 结果已拿到，取消尚未触发的定时器
        if self._cancel_timer is not None:
            self._cancel_timer.cancel()
            self._cancel_timer = None

    def feedback_callback(self, feedback_msg):
        """进度反馈回调。"""
        progress = feedback_msg.feedback.progress
        self.get_logger().info(f'反馈进度: {progress*100:.0f}%')

    def _on_cancel_done(self, future):
        """打印 cancel_goal_async 的返回结果。"""
        try:
            response = future.result()
        except Exception as e:
            self.get_logger().error(f'取消请求失败: {e}')
            return
        if response is None or not response.goals_canceling:
            self.get_logger().info('取消请求被忽略（目标可能已结束）')
        else:
            self.get_logger().info('取消请求已被接受')


def main(args=None):
    rclpy.init(args=args)

    distance = 5.0
    cancel_after = 0.0
    # 用法: ros2 run my_action_demo move_client [distance] [cancel_after_sec]
    # remove_ros_args 剔除 --ros-args 部分，避免把 ROS 参数当成业务参数
    argv = remove_ros_args(args=sys.argv)
    if len(argv) > 1:
        distance = float(argv[1])
    if len(argv) > 2:
        cancel_after = float(argv[2])

    node = MoveActionClient()
    try:
        node.send_goal(distance, cancel_after)
    except (KeyboardInterrupt, ExternalShutdownException):   # [可选]
        pass
    finally:
        # 兜底取消定时器，防止 send_goal 内异常时泄漏
        if node._cancel_timer is not None:
            node._cancel_timer.cancel()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

路径：`~/ros2_ws/src/my_action_demo/my_action_demo/move_client.py`

**预期**：`send_goal_async` 带 `feedback_callback`；取消分支只在 `cancel_after > 0` 时启用。

### 步骤 5 · 写 package.xml

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>my_action_demo</name>
  <version>0.1.0</version>
  <description>S1 模块3：自定义 Action 服务端/客户端</description>
  <maintainer email="lddzwxy@gmail.com">laoding</maintainer>
  <license>Apache-2.0</license>

  <depend>rclpy</depend>
  <depend>my_interfaces</depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

**预期**：`depend` 含 `my_interfaces`。

### 步骤 6 · 写 setup.py

```python
from setuptools import find_packages, setup

package_name = 'my_action_demo'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='laoding',
    maintainer_email='lddzwxy@gmail.com',
    description='S1 模块3：Action 示例',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'move_server = my_action_demo.move_server:main',
            'move_client = my_action_demo.move_client:main',
        ],
    },
)
```

**预期**：两条 `console_scripts` 与文件名一致。

### 步骤 7 · 写 setup.cfg

```ini
[develop]
script_dir=$base/lib/my_action_demo
[install]
install_scripts=$base/lib/my_action_demo
```

**预期**：包名三处一致。

### 步骤 8 · 编译

```bash
cd ~/ros2_ws
colcon build --symlink-install --packages-select my_action_demo
```

**预期**：

```text
Starting >>> my_action_demo
Finished <<< my_action_demo [0.71s]
Summary: 1 package finished
```

### 步骤 9 · source 并确认可执行

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 pkg executables my_action_demo
```

**预期**：

```text
my_action_demo move_client
my_action_demo move_server
```

### 步骤 10 · 双终端跑正常路径

终端 A：

```bash
ros2 run my_action_demo move_server
```

终端 B：

```bash
ros2 run my_action_demo move_client 5.0
```

**预期**：进度 10%→100% 连续打印；`结果: success=True, traveled=5.00 m`。

### 步骤 11 · 演示取消

终端 B 重新跑：

```bash
ros2 run my_action_demo move_client 5.0 2.0
```

**预期**：

- 约 2 秒后 `2.0s 后请求取消…`；
- server 打印 `收到取消请求`、`已取消，已走 X.XX m`；
- client 打印 `结果: success=False, traveled=X.XX m`。

### 步骤 12 · 测拒绝路径

```bash
ros2 run my_action_demo move_client -1.0
```

**预期**：server 打印 `拒绝目标：distance 必须 > 0`；client 打印 `目标被拒绝`。

---

## 五、关键 API / 命令详解

| 名称 | 作用 |
| ---- | ---- |
| `ActionServer(self, Type, name, execute_callback=..., goal_callback=..., cancel_callback=...)` | 建动作服务端 |
| `GoalResponse.ACCEPT / REJECT` | goal_callback 返回值 |
| `CancelResponse.ACCEPT / REJECT` | cancel_callback 返回值 |
| `goal_handle.request` | 取 goal 字段 |
| `goal_handle.publish_feedback(fb)` | 发进度 |
| `goal_handle.is_cancel_requested` | 是否有人请求取消 |
| `goal_handle.canceled()` | 标记已取消 |
| `goal_handle.succeed()` | 标记成功 |
| `ActionClient(self, Type, name)` | 建动作客户端 |
| `client.wait_for_server()` | 等服务端上线 |
| `client.send_goal_async(goal, feedback_callback=cb)` | 发目标（异步） |
| `goal_handle.get_result_async()` | 等最终结果 |
| `goal_handle.cancel_goal_async()` | 请求取消 |

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| 取消不生效 | execute 里没检查 `is_cancel_requested` | 循环里检查并 `canceled()` |
| `ModuleNotFoundError: my_interfaces` | 接口包没编译 / 没 source | `colcon build --packages-select my_interfaces` + source |
| 进度一直不动 | 忘了 `publish_feedback` | 见步骤 3 代码 |
| execute 卡死不回反馈 | 循环里阻塞太久 / 没 sleep 就空转 | `time.sleep(0.1)`，保持循环轻量 |
| `目标被拒绝` | `distance <= 0` | 改用正数 |
| `Executable 'move_server' not found` | entry_points 错 / 未 build | 核对 setup.py，重新 build |
| 取消后 result 仍是 success=True | 没在取消分支填 result | 取消分支也要 `return result` |

---

## 七、预期输出汇总

1. `ros2 run my_action_demo move_server` 打印已就绪；
2. `move_client 5.0`：进度连续到 100%，`success=True`；
3. `move_client 5.0 2.0`：中途取消，`success=False`，`traveled` 小于 5；
4. `move_client -1.0`：目标被拒绝；
5. `ros2 action list` 能看到 `/move_distance`（进阶验证）。

---

## 八、小作业（5 分钟）

1. 把模拟速度调快，观察总时长变短：

   ```bash
   ros2 run my_action_demo move_server --ros-args -p speed_mps:=1.0
   ```

   预期：5 米任务约 5 秒完成（默认 0.2 m/s 要约 25 秒）。

2. 用 `ros2 action info /move_distance` 查看当前 goal 数量（可选，需 `ros2action` 插件）。

---

## 九、下集预告

模块 3 收工。下集做一次**设计决策**：为"送货小车"需求清单逐条标注 Topic / Service / Action，整理出你自己的接口设计表。
