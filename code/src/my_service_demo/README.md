# my_service_demo

S1 模块 3 教学包：自定义 Service 服务端/客户端（`/set_mode` 一问一答）。

## 版本卡

| 项 | 版本 |
| -- | ---- |
| OS | Ubuntu 24.04 LTS (Noble) / WSL2 |
| ROS | ROS2 Jazzy Jalisco |
| Python | 3.12 |
| 工作空间 | ~/ros2_ws |
| 包版本 | 0.1.0 |

## 依赖

见 `package.xml`（含 `my_interfaces`，先编译接口包）。安装：

```bash
cd ~/ros2_ws
rosdep install --from-paths src -y --ignore-src
```

## 编译

```bash
cd ~/ros2_ws
colcon build --packages-select my_service_demo --symlink-install
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

## 启动

```bash
# 终端 1：服务端
ros2 run my_service_demo service_server

# 终端 2：客户端（参数为目标模式 manual / auto / sport，默认 auto）
ros2 run my_service_demo service_client auto

# 或直接用 CLI
ros2 service call /set_mode my_interfaces/srv/SetMode "{mode: 'auto'}"
```

**预期**：客户端打印 `响应: success=True, message=mode set to auto`；传非法模式返回 `success=False` 并列出白名单。

## 节点表

| 节点 | 角色 | 服务 | 说明 |
| ---- | ---- | ---- | ---- |
| mode_service_server | 服务端 | /set_mode (my_interfaces/srv/SetMode) | 白名单 manual / auto / sport |
| mode_service_client | 客户端 | 调用 /set_mode | 命令行传目标模式，默认 auto |

## 调试

```bash
ros2 node list                          # /mode_service_server
ros2 service list                       # /set_mode
ros2 service type /set_mode             # my_interfaces/srv/SetMode
ros2 service call /set_mode my_interfaces/srv/SetMode "{mode: 'sport'}"
```
