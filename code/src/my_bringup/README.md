# my_bringup

S1 模块 4 教学包：参数、Launch、多节点小系统（感知 → 决策 → 执行）。

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
colcon build --packages-select my_bringup --symlink-install
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

## 启动

```bash
ros2 launch my_bringup demo_system.launch.py
```

**预期**：4 节点同屏输出——`sim_sensor` 发 `/detection`、`decision_node` 决策发 `/cmd_vel`、`mock_driver` 打印执行、`param_node` 发 `/heartbeat`。

Lifecycle 演示（了解，单独运行）：

```bash
ros2 run my_bringup lifecycle_demo
# 另开终端走状态机
ros2 lifecycle set /lifecycle_demo configure
ros2 lifecycle set /lifecycle_demo activate     # 此时才开始发 /lc_heartbeat
```

## 节点表

| 节点 | 角色 | 发布 | 订阅 |
| ---- | ---- | ---- | ---- |
| sim_sensor | 感知 | /detection | — |
| decision_node | 决策 | /cmd_vel | /detection |
| mock_driver | 执行 | — | /cmd_vel |
| param_node | 参数演示 | /heartbeat | — |
| lifecycle_demo | Lifecycle 演示 | /lc_heartbeat | — |

## 参数

见 `config/params.yaml`。常用：

| 节点 | 参数 | 默认 | 说明 |
| ---- | ---- | ---- | ---- |
| param_node | publish_frequency | 5.0 | 心跳频率 Hz |
| param_node | topic_name | /heartbeat | 心跳话题名 |
| sim_sensor | publish_frequency | 5.0 | 检测发布频率 Hz |
| sim_sensor | min_distance | 0.2 | 模拟障碍最小距离 m |
| decision_node | stop_distance | 0.5 | 停车阈值 m |

## 调试

```bash
ros2 node list                              # 4 个节点（含 lifecycle_demo 则 5 个）
ros2 topic list                             # /detection /cmd_vel /heartbeat
ros2 topic hz /detection                    # 约 5 Hz
ros2 topic echo /cmd_vel --once
ros2 param get /param_node publish_frequency
```

rqt_graph / rqt_console / ros2 bag 见模块 5。
