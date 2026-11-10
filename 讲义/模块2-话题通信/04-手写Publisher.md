# 2.4 手写 Publisher（Python 3.12）

>  模块 2 第 4 集 
>  前置：已完成 2.3，会 `ros2 topic echo/hz`。 
>  本集开始新建包 `my_topic_demo`。仓库对照：`code/src/my_topic_demo/`。 

---

## 一、本集目标

手写定时发布 `Twist` 到 `/cmd_vel`，完成：

`建包 → 写代码 → 配置 → colcon build → source → 运行 → echo 验证`。

理解 `create_publisher` / `create_timer` / `rclpy.spin` 为什么这样配合。

---

## 二、效果演示

终端 A：

```bash
ros2 run my_topic_demo velocity_publisher
```

终端 B：

```bash
ros2 topic echo /cmd_vel
```

**预期**：速度每 0.1 秒一条，`linear.x` 在 0.05~0.25 缓慢变化，`angular.z` 正弦摆动：

```text
linear:
  x: 0.21
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.12
```

---

## 三、理论讲解

### 3.1 为什么用 timer 而不是 `while + sleep`？

```python
# 不推荐：死循环占满 CPU，且 sleep 误差会累积
while rclpy.ok():
    publisher.publish(msg)
    time.sleep(0.1)
```

ROS2 提供**定时器**（`create_timer`）：

- 由 `spin` 的事件循环调度，不空转；
- 到点才回调 `timer_callback`，回调里只管组包、发布；
- 和订阅回调共用同一套调度，后续加订阅不会打架。

### 3.2 节点里三件套的分工

| 时机 | 干什么 |
| ---- | ------ |
| 构造函数 | 声明参数、创建 publisher / timer |
| 回调 | 组消息、`publish`、打日志 |
| `main` | `init` → `spin` → `destroy_node` → `shutdown` |

### 3.3 为什么消息里的速度在变？

固定值不好观察。我们让：

- `linear.x = 0.15 + 0.1 * sin(t * 0.5)`：在 0.05~0.25 缓慢爬行；
- `angular.z = 0.3 * sin(t * 0.3)`：左右摆头。

这样 `echo` 一眼能看出"数据在动"。

### 3.4 参数先 declare 再 get

`declare_parameter('publish_frequency', 10.0)` 的作用：

1. 注册默认值 10.0 Hz；
2. 允许启动时覆盖：`ros2 run ... --ros-args -p publish_frequency:=5.0`；
3. 不 declare 就 `get_parameter` 会抛异常（Jazzy 默认 `allow_undeclared_parameters=false`）。

---

## 四、实操步骤（手把手）

> 本集开始新建包 `my_topic_demo`。仓库对照：`code/src/my_topic_demo/`。 

### 步骤 0 · 打开终端

Windows Terminal → Ubuntu。

**预期**：`<用户名>@<电脑名>:~$` 提示符。

### 步骤 1 · 创建包目录

```bash
cd ~/ros2_ws/src
ros2 pkg create my_topic_demo --build-type ament_python --dependencies rclpy geometry_msgs --node-name velocity_publisher
```

**预期**：`find my_topic_demo -type f | sort` 至少看到：

```text
my_topic_demo/my_topic_demo/__init__.py
my_topic_demo/my_topic_demo/velocity_publisher.py
my_topic_demo/package.xml
my_topic_demo/resource/my_topic_demo
my_topic_demo/setup.cfg
my_topic_demo/setup.py
```

### 步骤 2 · 写 velocity_publisher.py

**设计动机**：

- 类继承 `Node`，后面加订阅、加参数都方便；
- 参数化话题名和频率，CLI 可覆盖；
- 用 timer 驱动发布，频率稳定；
- 日志节流，避免刷屏。

完整代码（与仓库 `code/src/my_topic_demo/my_topic_demo/velocity_publisher.py` 一致）：

```python
#!/usr/bin/env python3
# 速度指令发布者：按频率发布 geometry_msgs/Twist 到 /cmd_vel
# 教学点：create_publisher、create_timer、declare_parameter、spin

import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class VelocityPublisher(Node):
    """定时发布速度指令，模拟遥控或自动控制。"""

    def __init__(self):
        super().__init__('velocity_publisher')

        # 声明参数：发布频率（Hz）与目标话题名
        self.declare_parameter('publish_frequency', 10.0)
        self.declare_parameter('topic_name', '/cmd_vel')

        frequency = self.get_parameter('publish_frequency').value
        topic_name = self.get_parameter('topic_name').value

        # 创建发布者：类型、话题、QoS 队列深度
        self.publisher_ = self.create_publisher(Twist, topic_name, 10)

        # 定时器驱动发布，保证频率稳定（比 while+sleep 更规范）
        # 频率做下限保护，防止 0/负数导致除零
        timer_period = 1.0 / max(frequency, 0.1)
        self.timer_period = timer_period
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.elapsed = 0.0
        self.tick = 0

        self.get_logger().info(
            f'开始发布速度到 {topic_name}，频率 {frequency} Hz')

    def timer_callback(self):
        """每隔 timer_period 发一条速度指令。"""
        msg = Twist()
        # 线速度在 0.05~0.25 之间缓慢变化，便于观察
        msg.linear.x = 0.15 + 0.1 * math.sin(self.elapsed * 0.5)
        # 角速度正弦摆动：车会左右画弧
        msg.angular.z = 0.3 * math.sin(self.elapsed * 0.3)

        self.publisher_.publish(msg)
        # 按真实经过时间累加（与 publish_frequency 联动），波形快慢才正确
        self.elapsed += self.timer_period
        self.tick += 1

        # 日志节流：避免刷屏（每 20 次打一条）
        if self.tick % 20 == 0:
            self.get_logger().info(
                f'发速度: linear.x={msg.linear.x:.2f}, angular.z={msg.angular.z:.2f}')


def main(args=None):
    rclpy.init(args=args)
    node = VelocityPublisher()
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
~/ros2_ws/src/my_topic_demo/my_topic_demo/velocity_publisher.py
```

**预期**：保存无语法红线；缩进全是 4 空格（PEP8）。

### 步骤 3 · 写 package.xml

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>my_topic_demo</name>
  <version>0.1.0</version>
  <description>S1 模块2：/cmd_vel 速度指令发布与订阅示例</description>
  <maintainer email="laoding@gmail.com">laoding</maintainer>
  <license>Apache-2.0</license>

  <depend>rclpy</depend>
  <depend>geometry_msgs</depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

路径：`~/ros2_ws/src/my_topic_demo/package.xml`

**预期**：`depend` 含 `rclpy` 与 `geometry_msgs`。

### 步骤 4 · 写 setup.py

```python
from setuptools import find_packages, setup

package_name = 'my_topic_demo'

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
    maintainer_email='laoding@gmail.com',
    description='S1 模块2：/cmd_vel 发布与订阅',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'velocity_publisher = my_topic_demo.velocity_publisher:main',
        ],
    },
)
```

> `velocity_publisher = my_topic_demo.velocity_publisher:main` 三段含义： 
> 可执行名 = 包.模块:函数。

路径：`~/ros2_ws/src/my_topic_demo/setup.py`

**预期**：可执行名与文件名一致（`velocity_publisher` → `velocity_publisher.py`）。

### 步骤 5 · 写 setup.cfg

```ini
[develop]
script_dir=$base/lib/my_topic_demo
[install]
install_scripts=$base/lib/my_topic_demo
```

路径：`~/ros2_ws/src/my_topic_demo/setup.cfg`

**预期**：`my_topic_demo` 三处包名拼写一致。

### 步骤 6 · 编译

```bash
cd ~/ros2_ws
colcon build --symlink-install --packages-select my_topic_demo
```

**预期**：

```text
Starting >>> my_topic_demo
Finished <<< my_topic_demo [0.63s]
Summary: 1 package finished
```

失败时看：`less log/latest_build/my_topic_demo/stdout_stderr.log`

### 步骤 7 · source 环境

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

**预期**：`ros2 pkg executables my_topic_demo` 显示

```text
my_topic_demo velocity_publisher
```

### 步骤 8 · 运行 Publisher

```bash
ros2 run my_topic_demo velocity_publisher
```

**预期**：终端输出类似

```text
[INFO] [velocity_publisher]: 开始发布速度到 /cmd_vel，频率 10.0 Hz
[INFO] [velocity_publisher]: 发速度: linear.x=0.15, angular.z=0.00
[INFO] [velocity_publisher]: 发速度: linear.x=0.24, angular.z=0.09
```

按 `Ctrl+C` 停。

### 步骤 9 · 另开终端验证话题

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 topic echo /cmd_vel
ros2 topic hz /cmd_vel
```

（在 publisher 运行时）**预期**：

- echo：`linear.x` 在 0.05~0.25 变化，`angular.z` 在 -0.3~0.3 摆动；
- hz：`average rate` 约 **10 Hz**。

### 步骤 10 · 覆盖参数试试

```bash
ros2 run my_topic_demo velocity_publisher --ros-args -p publish_frequency:=2.0
```

**预期**：日志写 `频率 2.0 Hz`，`hz` 降到约 2。

---

## 五、关键 API / 命令详解

| 名称 | 作用 |
| ---- | ---- |
| `super().__init__('velocity_publisher')` | 创建节点并注册节点名 |
| `declare_parameter(name, default)` | 声明参数与默认值 |
| `get_parameter(name).value` | 读取参数当前值 |
| `create_publisher(Twist, topic, 10)` | 建发布者：类型 / 话题 / QoS 深度 |
| `create_timer(period, callback)` | 建定时器，到点调回调 |
| `publisher_.publish(msg)` | 发出一条消息 |
| `get_logger().info(...)` | 打日志（带节点名前缀） |
| `rclpy.spin(node)` | 事件循环：驱动 timer 与订阅回调 |
| `rclpy.init / shutdown` | 进程级初始化 / 清理 |

参数覆盖命令：

```bash
-p publish_frequency:=5.0
-p topic_name:=/robot1/cmd_vel
```

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| 程序立刻退出，无任何打印 | 只写了 publish 没 `spin` | 必须 `rclpy.spin(node)` |
| `ImportError: cannot import name 'Twist'` | import 路径写错 | 正确：`from geometry_msgs.msg import Twist` |
| `ParameterNotDeclaredException` | 没 declare 就 get | 先 `declare_parameter` |
| `Package 'my_topic_demo' not found` | 没 build 或没 source | `colcon build` + source 两层 |
| `Executable 'velocity_publisher' not found` | entry_points 写错 / 未重编译 | 核对 `setup.py`，重新 build |
| 改了 .py 没生效 | 未用 symlink 或进程没重启 | `--symlink-install` + 重新 run |
| hz 远低于设定频率 | 回调里做了重活或日志刷屏 | 保持回调短小；节流日志 |

---

## 七、预期输出汇总

1. `colcon build` Summary 成功；
2. `ros2 run my_topic_demo velocity_publisher` 打印开始发布；
3. `ros2 topic echo /cmd_vel` 看到变化中的速度；
4. `ros2 topic hz /cmd_vel` 约 10 Hz；
5. `-p publish_frequency:=2.0` 后频率变 2 Hz。

---

## 八、小作业（5 分钟）

1. 把 `angular.z` 改成**方波**摆动（正负交替，每 1 秒切换），`echo` 里看到"急转"：

   ```python
   msg.angular.z = 0.3 if int(self.elapsed) % 2 == 0 else -0.3
   ```

2. 用 `--ros-args -p topic_name:=/demo_vel` 发布到别的话题，`ros2 topic list` 确认多了一个 `/demo_vel`。

---

## 九、下集预告

有喊话的了，下集写**接听的 Subscriber**：订阅 `/cmd_vel`、解析 `linear.x / angular.z`，并学会"回调要短小"这条铁律。
