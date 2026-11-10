# my_action_demo

S1 模块 3 教学包：自定义 Action 服务端/客户端（`/move_distance` 长时任务，带反馈、可取消）。

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
colcon build --packages-select my_action_demo --symlink-install
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

## 启动

```bash
# 终端 1：Action 服务端
ros2 run my_action_demo move_server

# 终端 2：发送目标（前进 5 m），用法: move_client [distance] [cancel_after_sec]
ros2 run my_action_demo move_client 5.0

# 2 秒后中途取消的示例
ros2 run my_action_demo move_client 5.0 2.0
```

**预期**：客户端周期打印 `反馈进度: N%`，最终 `结果: success=True, traveled=5.00 m`；取消示例会打 `已取消，已走 x.xx m`。

## 节点表

| 节点 | 角色 | 动作 | 说明 |
| ---- | ---- | ---- | ---- |
| move_action_server | 服务端 | /move_distance (my_interfaces/action/MoveDistance) | 按速度模拟里程累加，支持反馈/取消 |
| move_action_client | 客户端 | 调用 /move_distance | 发目标、收反馈，可定时取消 |

## 参数

| 节点 | 参数 | 默认 | 说明 |
| ---- | ---- | ---- | ---- |
| move_action_server | speed_mps | 0.2 | 模拟速度 m/s（必须 > 0） |

## 调试

```bash
ros2 node list                              # /move_action_server
ros2 action list                            # /move_distance
ros2 action info /move_distance
ros2 action send_goal /move_distance my_interfaces/action/MoveDistance "{distance: 2.0}" --feedback
```
