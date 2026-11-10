# 模块 7 · Gazebo Harmonic 仿真（细纲 · 6 集）

> 目标：小车在 Gazebo Harmonic 中稳定显示、差速驱动、带传感器、可遥控。 
> 前置：模块 6 的 `my_car_description`。 
> 产出包：`my_car_gazebo`（world / launch / bridge / teleop）。 
> 钉死：**Gazebo Harmonic + `ros-jazzy-ros-gz*` + `gz sim`**，禁用 Classic。

---

## 7.1 Gazebo 安装与界面

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 装好 ros_gz，`gz sim` 能起空世界 |
| 开场演示 | `gz sim` 起世界；WSLg 下能鼠标旋转 |
| 知识点 | ① `ros-jazzy-ros-gz` / `ros-jazzy-ros-gz-sim` / `ros-jazzy-ros-gz-bridge` ② `gz sim` vs Classic `gazebo` ③ WSLg 图形 ④ worlds 资源 |
| 跟做步骤 | **1** `sudo apt install -y ros-jazzy-ros-gz`<br>**2** `source /opt/ros/jazzy/setup.bash`<br>**3** `gz sim -r empty.sdf`（或 `ros2 launch ros_gz_sim gz_sim.launch.py`）<br>**4** 确认窗口、相机可动<br>**5** `ros2 run ros_gz_sim create --help` 检查 |
| 常见坑 | Classic 与 Harmonic 混用（命令/包名错）；WSLg 黑屏（驱动/mesa、重启 WSL）；未装 ros-gz 与 ROS 不集成 |
| 预期输出 | Gazebo 窗口可见空世界 |
| 小作业 | 记下你启动空世界的命令 |
| 下集预告 | 把 URDF 小车塞进这个世界 |

---

## 7.2 URDF 拉进仿真

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | `ros_gz_sim create` 生成模型且不飞走 |
| 开场演示 | 小车静止在地面，可平移视角 |
| 知识点 | ① robot_state_publisher + /robot_description ② `ros_gz_sim create -topic robot_description` ③ spawn 高度/姿态 ④ inertial 必须正确 ⑤ 尺寸/单位 |
| 跟做步骤 | **1** 启动 gz 空世界<br>**2** `ros2 run robot_state_publisher robot_state_publisher`（用 xacro 参数）<br>**3** `ros2 run ros_gz_sim create -topic robot_description -name my_car -z 0.1`<br>**4** 观察是否落地稳定<br>**5** 抽成 launch |
| 关键命令 | `ros2 run ros_gz_sim create -topic robot_description -name my_car -z 0.1` |
| 常见坑 | 缺 plugin 不会动（下集）；inertial=0 飞走；重力关了；z=0 陷入地下 |
| 预期输出 | 车静止在地；无爆炸 |
| 小作业 | 把车改成红色 visual 并重新 spawn |
| 下集预告 | 差速插件 + /cmd_vel 让它动 |

---

## 7.3 差速小车与 cmd_vel

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | diff_drive 插件接 `/cmd_vel`，发 `/odom` |
| 开场演示 | teleop 一按，车平滑前进转向 |
| 知识点 | ① gz 侧 `gz-sim-diff-drive-system` ② 轮参数：wheel_separation、wheel_radius ③ 话题桥 `/cmd_vel`、`/odom` ④ 契约类型 geometry_msgs/Twist、nav_msgs/Odometry |
| 跟做步骤 | **1** 在 xacro/gazebo 标签加 diff_drive（左右轮 joint 名、轮距、轮径）<br>**2** `config/bridge.yaml` 或参数把 `/cmd_vel`、`/odom` 接到 ros_gz_bridge<br>**3** launch 起 world + spawn + bridge + rsp<br>**4** `ros2 run teleop_twist_keyboard teleop_twist_keyboard`<br>**5** `ros2 topic echo /odom` |
| 关键插件 | diff_drive system；ros_gz_bridge 参数桥 |
| 常见坑 | 轮参数与 URDF 不一致（原地打滑/跑偏）；bridge 类型写错；话题名不是 /cmd_vel |
| 预期输出 | 键盘控制车走动；/odom 有数据且 child_frame_id=base_link |
| 小作业 | 设 linear.x=0.2 用 `ros2 topic pub` 让车直行 5 秒 |
| 下集预告 | 给车装眼睛（相机）和雷达 |

---

## 7.4 传感器：相机与雷达

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 仿真相机 Image、雷达 LaserScan、IMU；frame 与 TF 一致 |
| 开场演示 | RViz2 显示 LaserScan 点云扇 + rqt_image_view 相机 |
| 知识点 | ① lidar / camera / imu 插件 ② frame 名必须与 TF 一致 ③ 话题 `/scan` `/camera/image` `/imu` ④ bridge QoS（传感器常 Best Effort） |
| 跟做步骤 | **1** xacro 加 gpu_lidar / camera / imu 传感器插件与 link<br>**2** bridge 接 `/scan`、图像、`/imu`<br>**3** RViz2 加 LaserScan（frame laser）<br>**4** `ros2 topic echo /scan --once` 看 ranges<br>**5** 对照 CONTRACT：frame=laser |
| 常见坑 | sensor frame 与 TF 不一致（RViz 全空）；桥类型不匹配；忘记 use_sim_time |
| 预期输出 | /scan 有距离数组；RViz 扇形可见 |
| 小作业 | 在车前放一个 box，确认 laser 能扫到 |
| 下集预告 | 了解 ros2_control 分层（本课用插件验收） |

---

## 7.5 ros2_control（了解）

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 理解控制器分层：hardware interface / controller / manager |
| 开场演示 | `ros2 control list_controllers` 概念图（可不在 Gazebo 深跑） |
| 知识点 | ① 为何工程上用 ros2_control ② spawn_controller ③ 与 diff_drive 插件路径的取舍 ④ 本课验收走插件路径 |
| 跟做步骤 | 概念讲解 + 若环境顺利可展示 controller manager；失败不阻塞 |
| 常见坑 | 以为必须 ros2_control 才能动；未 spawn controller 就发指令 |
| 预期输出 | 能说出插件路径与 ros2_control 路径的区别 |
| 小作业 | 在笔记画一张分层图 |
| 下集预告 | teleop + 里程计 + RViz 总集成 |

---

## 7.6 teleop + 里程计

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 手一按车就动；RViz 同时看 TF 与激光；use_sim_time 一致 |
| 开场演示 | 三窗口：Gazebo / teleop / RViz |
| 知识点 | ① teleop_twist_keyboard ② use_sim_time 全链路 true ③ RViz Fixed Frame=odom ④ TF + LaserScan + RobotModel |
| 跟做步骤 | **1** `ros2 launch my_car_gazebo gazebo.launch.py`（内部 use_sim_time）<br>**2** teleop<br>**3** RViz Fixed Frame=odom，加 TF/LaserScan/RobotModel<br>**4** 绕障碍一圈<br>**5** `ros2 topic hz /odom /scan` |
| 常见坑 | use_sim_time 不一致导致 TF extrapolation / 时间跳变；teleop 默认话题不是 /cmd_vel（用 remap） |
| 预期输出 | 遥控绕圈；RViz 激光与 TF 同步 |
| 小作业 | 录 bag：/cmd_vel /odom /scan，供模块 8 复现 |
| 下集预告 | 模块 8：送货综合项目 |

---

## 本模块代码演进

| 集 | 对 `code/` 的改动 |
| -- | ----------------- |
| 7.1 | （安装验证，无包） |
| 7.2 | `src/my_car_gazebo/` + spawn launch |
| 7.3 | diff_drive + bridge + teleop 路径 |
| 7.4 | 传感器插件与 bridge |
| 7.6 | gazebo.launch.py 总装 + rviz |

> 配套讲义：`讲义/模块7-Gazebo仿真/01–06`。 
> 配套代码：`code/src/my_car_gazebo/`，模型来自 `my_car_description`。
