# 3.3 Service Server / Client

> 模块 3 第 3 集 
> 前置：已完成 3.2，`my_interfaces` 已编译并 source。 
> 本集开始新建包 `my_service_demo`，仓库对照：`code/src/my_service_demo/`。 

---

## 一、本集目标

实现 `/set_mode` 服务端与客户端：

- `create_service` / `create_client`；
- 回调签名 `(request, response) → response`；
- `wait_for_service` + `call_async` + `spin_until_future_complete`；
- 分清**同步阻塞**与**异步等待**。

---

## 二、效果演示

终端 A：

```bash
ros2 run my_service_demo service_server
```

终端 B：

```bash
ros2 run my_service_demo service_client auto
```

**预期**：

```text
# 终端 A
[INFO] [mode_service_server]: 服务 /set_mode 已就绪
[INFO] [mode_service_server]: 收到设置模式请求: 'auto'
[INFO] [mode_service_server]: mode set to auto

# 终端 B
[INFO] [mode_service_client]: 响应: success=True, message=mode set to auto
```

非法模式：

```bash
ros2 run my_service_demo service_client turbo
```

**预期**：

```text
[INFO] [mode_service_server]: 收到设置模式请求: 'turbo'
[WARN] [mode_service_server]: invalid mode 'turbo', allowed: ('manual', 'auto', 'sport')
[INFO] [mode_service_client]: 响应: success=False, message=invalid mode 'turbo', allowed: ('manual', 'auto', 'sport')
```

---

## 三、理论讲解

### 3.1 服务端：守着一个"业务窗口"

```text
create_service(SetMode, '/set_mode', callback)
```

含义：在 `/set_mode` 开一个窗口，凡是有 `SetMode` 类型的请求进来，就调 `callback`。

### 3.2 回调签名

```python
def set_mode_callback(self, request, response):
    # request：客户端发来的内容（只读取）
    # response：你要填好并返回的内容
    response.success = True
    response.message = '...'
    return response   # 必须 return
```

| 参数 | 方向 | 你干什么 |
| ---- | ---- | -------- |
| `request` | 客户端 → 服务端 | 读 `request.mode` |
| `response` | 服务端 → 客户端 | 填 `success` / `message`，`return` |

### 3.3 客户端三步走

```python
# 1) 等服务上线（server 没起来就干等）
while not self.client.wait_for_service(timeout_sec=1.0):
    ...

# 2) 异步发请求（不阻塞本线程）
future = self.client.call_async(self.request)

# 3) 等结果（驱动事件循环直到 future 完成）
rclpy.spin_until_future_complete(self, future)
```

为什么用 `call_async` 而不是 `call`？

- `call()` 会**阻塞当前线程**直到响应；
- 在节点回调里再同步 `call`，容易**死锁**（回调在 spin 里，spin 被占住）；
- `call_async` + `spin_until_future_complete` 是 rclpy 推荐写法。

### 3.4 同步 vs 异步

| 写法 | 特点 | 风险 |
| ---- | ---- | ---- |
| `client.call(req)` | 简单，一行拿结果 | 阻塞；回调里用易死锁 |
| `call_async` + `spin_until_future_complete` | 推荐，可控 | 稍多两行 |
| `call_async` + 自己轮询 `future.done()` | 灵活 | 要自己写循环 |

---

## 四、实操步骤（手把手）

> 本集开始新建包 `my_service_demo`，仓库对照：`code/src/my_service_demo/`。 

### 步骤 0 · 打开终端

Windows Terminal → Ubuntu。

**预期**：`<用户名>@<电脑名>:~$` 提示符。

### 步骤 1 · 确认接口包可用

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 interface show my_interfaces/srv/SetMode
```

**预期**：能看到 `string mode` / `bool success` / `string message`。 
若报错，先回 3.2 编译 `my_interfaces` 并 source。

### 步骤 2 · 创建包

```bash
cd ~/ros2_ws/src
ros2 pkg create my_service_demo --build-type ament_python --dependencies rclpy my_interfaces --node-name service_server
```

**预期**：`my_service_demo` 目录出现。

### 步骤 3 · 写 service_server.py 

**设计动机**：

- 服务名 `/set_mode`，类型 `SetMode`；
- 白名单校验 mode，合法才切换；
- response 里永远填 `success` + `message`，客户端不用猜。

完整代码（与仓库 `code/src/my_service_demo/my_service_demo/service_server.py` 一致）：

```python
#!/usr/bin/env python3
# Service 服务端：提供 /set_mode（my_interfaces/srv/SetMode）
# 教学点：create_service、回调填 response、参数校验

import rclpy
from rclpy.node import Node

from my_interfaces.srv import SetMode


class ModeServiceServer(Node):
    """接收模式切换请求，校验后返回 success/message。"""

    # 允许的模式白名单
    ALLOWED_MODES = ('manual', 'auto', 'sport')

    def __init__(self):
        super().__init__('mode_service_server')
        self.current_mode = 'manual'

        # 创建服务：类型、服务名、回调
        self.srv = self.create_service(
            SetMode, '/set_mode', self.set_mode_callback)

        self.get_logger().info('服务 /set_mode 已就绪')

    def set_mode_callback(self, request: SetMode.Request,
                          response: SetMode.Response):
        """请求-响应回调：只做校验与状态更新，不要在里面再同步 call 别的服务。"""
        mode = request.mode
        self.get_logger().info(f'收到设置模式请求: {mode!r}')

        if mode in self.ALLOWED_MODES:
            self.current_mode = mode
            response.success = True
            response.message = f'mode set to {mode}'
            self.get_logger().info(response.message)
        else:
            response.success = False
            response.message = (
                f'invalid mode {mode!r}, allowed: {self.ALLOWED_MODES}')
            self.get_logger().warning(response.message)

        return response


def main(args=None):
    rclpy.init(args=args)
    node = ModeServiceServer()
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

路径：`~/ros2_ws/src/my_service_demo/my_service_demo/service_server.py`

**预期**：`create_service` 三参数：类型、服务名、回调。

### 步骤 4 · 写 service_client.py

完整代码（与仓库一致）：

```python
#!/usr/bin/env python3
# Service 客户端：调用 /set_mode，演示异步调用与结果等待
# 教学点：create_client、wait_for_service、call_async、spin_until_future_complete

import sys

import rclpy
from rclpy.node import Node
from rclpy.utilities import remove_ros_args

from my_interfaces.srv import SetMode


class ModeServiceClient(Node):
    """示例客户端：把命令行参数作为目标模式发给服务端。"""

    def __init__(self):
        super().__init__('mode_service_client')
        self.client = self.create_client(SetMode, '/set_mode')

        # 等待服务端上线，避免一上来就 call 失败
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('等待 /set_mode 服务上线...')

        self.request = SetMode.Request()

    def send_request(self, mode: str):
        """异步发送请求并等待结果。"""
        self.request.mode = mode
        # call_async 不阻塞当前线程；再用 spin 等 future
        future = self.client.call_async(self.request)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            response = future.result()
            self.get_logger().info(
                f'响应: success={response.success}, message={response.message}')
            return response
        self.get_logger().error('服务调用失败')
        return None


def main(args=None):
    rclpy.init(args=args)

    # 从命令行读模式，默认 auto
    # remove_ros_args 剔除 --ros-args 部分，避免把 ROS 参数当成业务参数
    argv = remove_ros_args(args=sys.argv)
    mode = 'auto'
    if len(argv) > 1:
        mode = argv[1]

    node = None
    try:
        # 构造函数里会等待服务上线，放进 try 里才能用 Ctrl+C 干净退出
        node = ModeServiceClient()
        node.send_request(mode)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

路径：`~/ros2_ws/src/my_service_demo/my_service_demo/service_client.py`

**预期**：`call_async` 后必须 `spin_until_future_complete`，否则拿不到结果。

### 步骤 5 · 写 package.xml

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>my_service_demo</name>
  <version>0.1.0</version>
  <description>S1 模块3：自定义 Service 服务端/客户端</description>
  <maintainer email="lddzwxy@gmail.com">laoding</maintainer>
  <license>Apache-2.0</license>

  <depend>rclpy</depend>
  <depend>my_interfaces</depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

路径：`~/ros2_ws/src/my_service_demo/package.xml`

**预期**：`depend` 含 **`my_interfaces`**（不是 `rosidl_*`）。

### 步骤 6 · 写 setup.py

```python
from setuptools import find_packages, setup

package_name = 'my_service_demo'

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
    description='S1 模块3：Service 示例',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'service_server = my_service_demo.service_server:main',
            'service_client = my_service_demo.service_client:main',
        ],
    },
)
```

路径：`~/ros2_ws/src/my_service_demo/setup.py`

**预期**：`console_scripts` 两条，可执行名与文件名一致。

### 步骤 7 · 写 setup.cfg

```ini
[develop]
script_dir=$base/lib/my_service_demo
[install]
install_scripts=$base/lib/my_service_demo
```

**预期**：包名三处一致。

### 步骤 8 · 编译

```bash
cd ~/ros2_ws
colcon build --symlink-install --packages-select my_service_demo
```

**预期**：

```text
Starting >>> my_service_demo
Finished <<< my_service_demo [0.65s]
Summary: 1 package finished
```

### 步骤 9 · source 并确认可执行

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 pkg executables my_service_demo
```

**预期**：

```text
my_service_demo service_client
my_service_demo service_server
```

### 步骤 10 · 双终端运行

终端 A：

```bash
ros2 run my_service_demo service_server
```

终端 B：

```bash
ros2 run my_service_demo service_client auto
```

**预期**：见"二、效果演示"。

### 步骤 11 · 第三终端观察服务

```bash
ros2 service list | grep set_mode
ros2 service type /set_mode
```

**预期**：

```text
/set_mode
my_interfaces/srv/SetMode
```

也可以手动 call（不跑 client）：

```bash
ros2 service call /set_mode my_interfaces/srv/SetMode "{mode: 'manual'}"
```

**预期**：终端 A 打印收到请求；call 返回 `success=True`。

---

## 五、关键 API / 命令详解

| 名称 | 作用 |
| ---- | ---- |
| `create_service(Type, name, callback)` | 注册服务端 |
| `callback(request, response) -> response` | 处理请求，必须 return response |
| `create_client(Type, name)` | 注册客户端 |
| `client.wait_for_service(timeout_sec=1.0)` | 等服务上线（返回 bool） |
| `client.call_async(request)` | 发请求，返回 future（不阻塞） |
| `rclpy.spin_until_future_complete(node, future)` | 驱动事件循环直到 future 完成 |
| `future.result()` | 取响应；失败可能为 None |
| `ros2 service call <名> <类型> <YAML>` | 命令行手动调用 |

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| `ModuleNotFoundError: my_interfaces` | 没编译接口包 / 没 source | `colcon build --packages-select my_interfaces` + source |
| `Service '/set_mode' is not available` | 没 `wait_for_service` 就 call | 加 `wait_for_service` 循环 |
| 客户端卡住没响应 | server 没起；或忘了 `spin_until_future_complete` | 先跑 server；补 spin |
| 节点死锁 / 不再响应 | 在回调里同步 `call` 另一个服务 | 用 `call_async`，别在回调里同步 call |
| `response` 全是默认值 | 回调忘了 `return response` | 必须 `return response` |
| `Executable 'service_server' not found` | entry_points 写错 / 未 build | 核对 setup.py，重新 build |
| 改了 SetMode.srv 字段没生效 | 改接口后只 source | 必须重新 `colcon build --packages-select my_interfaces` |

---

## 七、预期输出汇总

1. `ros2 service list` 有 `/set_mode`；
2. `service_client auto` → `success=True, message=mode set to auto`；
3. `service_client turbo` → `success=False, message=invalid mode ...`；
4. `ros2 service call /set_mode ... {mode: 'manual'}` 手动调用成功；
5. server 日志能看到每次请求。

---

## 八、小作业（5 分钟）

1. 给白名单增加模式 `eco`，非法时 message 里写明允许列表（提示：`self.ALLOWED_MODES = ('manual', 'auto', 'sport', 'eco')`）；
2. 用 `ros2 service call` 连发 `manual` / `auto` / `eco`，确认 server 的 `current_mode` 跟着变（看日志）。

---

## 九、下集预告

"前进 5 米"这种要跑几十秒、还要看进度、可能取消的任务，Service 扛不住。下集进入 **Action**：goal / feedback / result 三件套。
