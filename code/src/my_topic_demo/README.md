# my_topic_demo

S1 模块 2 教学包：`/cmd_vel` 速度指令的发布与订阅（话题通信）。

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
colcon build --packages-select my_topic_demo --symlink-install
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

## 启动

```bash
# 终端 1：发布者
ros2 run my_topic_demo velocity_publisher

# 终端 2：订阅者
ros2 run my_topic_demo velocity_subscriber
```

**预期**：订阅者每 20 条打印一次 `收到: linear.x=..., angular.z=...`；速度偏大会打 warning。

## 节点表

| 节点 | 角色 | 发布 | 订阅 |
| ---- | ---- | ---- | ---- |
| velocity_publisher | 发布者 | /cmd_vel (geometry_msgs/msg/Twist) | — |
| velocity_subscriber | 订阅者 | — | /cmd_vel (geometry_msgs/msg/Twist) |

## 参数

| 节点 | 参数 | 默认 | 说明 |
| ---- | ---- | ---- | ---- |
| velocity_publisher | publish_frequency | 10.0 | 发布频率 Hz |
| velocity_publisher | topic_name | /cmd_vel | 发布话题名 |
| velocity_subscriber | topic_name | /cmd_vel | 订阅话题名 |

```bash
# 运行时改频率
ros2 param set /velocity_publisher publish_frequency 2.0
```

## 调试

```bash
ros2 node list                       # /velocity_publisher /velocity_subscriber
ros2 topic list                      # 应含 /cmd_vel
ros2 topic hz /cmd_vel               # 约 10 Hz
ros2 topic echo /cmd_vel --once      # 看一条消息
ros2 topic info /cmd_vel             # 1 发布 / 1 订阅
```
