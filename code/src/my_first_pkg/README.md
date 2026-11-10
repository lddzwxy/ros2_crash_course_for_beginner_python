# my_first_pkg

S1 模块 1 教学包：第一个 ROS2 节点（Hello ROS2）。

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
colcon build --packages-select my_first_pkg --symlink-install
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

## 启动

```bash
ros2 run my_first_pkg hello_node
```

**预期**：终端打印 `Hello ROS2` 与欢迎语；Ctrl+C 退出。

## 节点表

| 节点 | 角色 | 发布 | 订阅 |
| ---- | ---- | ---- | ---- |
| hello_node | 入门节点 | — | — |

## 调试

```bash
ros2 node list              # 应看到 /hello_node
ros2 node info /hello_node
```
