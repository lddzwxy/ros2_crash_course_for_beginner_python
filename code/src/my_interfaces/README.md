# my_interfaces

S1 模块 3 接口包：自定义 msg / srv / action（ament_cmake + rosidl），被 `my_service_demo`、`my_action_demo` 依赖。

## 版本卡

| 项 | 版本 |
| -- | ---- |
| OS | Ubuntu 24.04 LTS (Noble) / WSL2 |
| ROS | ROS2 Jazzy Jalisco |
| Python | 3.12 |
| 工作空间 | ~/ros2_ws |
| 包版本 | 0.1.0 |

## 依赖

见 `package.xml`。安装：

```bash
cd ~/ros2_ws
rosdep install --from-paths src -y --ignore-src
```

## 编译

```bash
cd ~/ros2_ws
colcon build --packages-select my_interfaces
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

**注意**：修改 `.msg` / `.srv` / `.action` 后必须重新 `colcon build` 并重开终端 source，再编译依赖本包的 `my_service_demo` / `my_action_demo`。

## 使用方式

```bash
ros2 interface show my_interfaces/msg/RobotStatus
ros2 interface show my_interfaces/srv/SetMode
ros2 interface show my_interfaces/action/MoveDistance
```

## 接口表

| 接口 | 类型 | 字段 |
| ---- | ---- | ---- |
| my_interfaces/msg/RobotStatus | msg | `string status`、`float32 battery`、`uint8 mode`、`builtin_interfaces/Time stamp` |
| my_interfaces/srv/SetMode | srv | 请求 `string mode` → 响应 `bool success`、`string message` |
| my_interfaces/action/MoveDistance | action | 目标 `float32 distance` → 结果 `bool success`、`float32 distance_traveled`；反馈 `float32 progress` |

## 调试

```bash
ros2 interface list | grep my_interfaces   # 三个接口都在
ros2 interface proto my_interfaces/srv/SetMode
```
