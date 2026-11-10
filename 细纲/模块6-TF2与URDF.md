# 模块 6 · TF2 与机器人建模 URDF（细纲 · 6 集）

> 目标：理解坐标系，会建差速小车 URDF/Xacro，并在 RViz2 正确显示。 
> 前置：模块 2–5；有 ROS2 工具链。 
> 产出包：`my_car_description`（urdf + launch + rviz 配置）。 
> 契约 frame：`map → odom → base_link → {laser, camera_link, imu_link}`。

---

## 6.1 坐标系与 TF

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 理解 frame 与变换；map/odom/base_link 各自职责 |
| 开场演示 | RViz TF 树动画：车动，树跟着变 |
| 知识点 | ① 坐标系=名字+相对位姿 ② TF 树必须连通 ③ map 全局 / odom 里程计 / base_link 车体 ④ 传感器 frame 挂在车体下 ⑤ 不是"绝对坐标"而是相对链 |
| 跟做步骤 | 无建模实操；画契约树（对照 CONTRACT.md） |
| 常见坑 | 当成绝对坐标；frame 名打错导致树断裂 |
| 预期输出 | 能默画 map→odom→base_link→laser |
| 小作业 | 说出 `/odom` 消息里的 frame_id/child_frame_id 应该是什么 |
| 下集预告 | 怎么把变换发出去/查出来？ |

---

## 6.2 TF2 广播与监听

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 静态/动态 TF 广播；会用 view_frames、tf2_echo |
| 开场演示 | `ros2 run tf2_ros view_frames` 生成 PDF；`tf2_echo` 实时位姿 |
| 知识点 | ① `StaticTransformBroadcaster` / `TransformBroadcaster` ② `TransformListener` + Buffer ③ 时间戳与 extrapolation ④ 工具 `view_frames`、`tf2_echo` |
| 跟做步骤 | **1** 写小脚本或 demo：广播 `base_link→laser` 静态 TF<br>**2** 另一个节点广播动态 `odom→base_link`（正弦）<br>**3** `ros2 run tf2_ros tf2_echo odom base_link`<br>**4** `ros2 run tf2_ros view_frames`<br>**5** 故意断一路，看报错 |
| 关键 API | `TransformBroadcaster.sendTransform`、`StaticTransformBroadcaster`、`tf2_ros.Buffer/TransformListener` |
| 常见坑 | 时间戳 extrapolation（消息时间与 TF 不同步）；只发 odom→base_link 没有 base_link→laser |
| 预期输出 | view_frames 有连通树；tf2_echo 有数值 |
| 小作业 | 在 my_car_description 之前用 demo 验证 laser 外参 (0.1,0,0.2) |
| 下集预告 | 用 URDF 一次性描述整车 |

---

## 6.3 URDF 初识

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 看懂 link/joint/visual/collision/inertial |
| 开场演示 | 最小底盘盒子模型在 RViz 显示 |
| 知识点 | ① link=刚体 ② joint 连接与类型 ③ visual 看的 / collision 撞的 / inertial 物理 ④ 单位米/千克/弧度 ⑤ 轴向：x 前 y 左 z 上 |
| 跟做步骤 | **1** 建 `my_car_description` 包<br>**2** 写 `urdf/my_car.urdf.xacro` 第一版：base_link 盒子 + 两个轮子圆柱 + 前支撑球<br>**3** `check_urdf` 或 `ros2 run robot_state_publisher robot_state_publisher` + joint_state_publisher_gui + rviz<br>**4** RViz Fixed Frame 选 base_link，加 RobotModel |
| 关键标签 | `link`、`joint`、`origin xyz rpy`、`geometry box/cylinder/sphere`、`inertial mass/inertia` |
| 常见坑 | 轴向反了（轮子转错向）；单位 mm 当 m；没有 inertial（Gazebo 里飞） |
| 预期输出 | RViz 看到小车几何体 |
| 小作业 | 把底盘长宽改为 0.3×0.2 并刷新 RViz |
| 下集预告 | 一堆重复轮子，Xacro 参数化 |

---

## 6.4 Xacro 参数化

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 用 property/macro/include 复用建模 |
| 开场演示 | 改一个 `wheel_radius` 属性，两轮一起变 |
| 知识点 | ① `xacro:property` ② `xacro:macro` ③ `xacro:include` ④ 展开命令 `xacro file.urdf.xacro` ⑤ RViz/robot_state_publisher 吃展开后的 URDF |
| 跟做步骤 | **1** 抽 `wheel` 宏与 `base` 宏<br>**2** 属性：车长宽高、轮半径、轮距<br>**3** launch 里 `Command(['xacro ', PathJoinSubstitution([...])])`<br>**4** `xacro my_car.urdf.xacro > /tmp/car.urdf` 验证无报错 |
| 关键命令 | `xacro my_car.urdf.xacro` |
| 常见坑 | 没展开就丢给 RViz；宏参数漏传；include 路径错 |
| 预期输出 | 修改属性一次生效；xacro 无错误 |
| 小作业 | 加 camera_link 与 imu_link 静态几何 |
| 下集预告 | 在 RViz2 做完整自检 |

---

## 6.5 RViz2 检查模型

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | RobotModel + TF + LaserScan 一次配好；Fixed Frame 正确 |
| 开场演示 | display.launch.py 一键：GUI 调关节 + RViz |
| 知识点 | ① Fixed Frame 选 `base_link` 或 `odom` ② RobotModel Description Topic ③ TF 显示 ④ 保存 .rviz 配置 ⑤ joint_state_publisher_gui |
| 跟做步骤 | **1** `ros2 launch my_car_description display.launch.py`<br>**2** Fixed Frame=base_link<br>**3** Add RobotModel、TF<br>**4** 拖 GUI 看轮子转<br>**5** 保存 rviz 配置到包内并 data_files 安装 |
| 常见坑 | Fixed Frame 选 map 但没人发 map TF（全空）；Description Topic 不是 `/robot_description` |
| 预期输出 | 模型完整、TF 树 base_link→wheels/laser |
| 小作业 | 导出 URDF 截图到作业笔记 |
| 下集预告 | 建模常见坑合集 |

---

## 6.6 建模坑合集

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 独立修 URDF：visual/collision/inertial 问题 |
| 开场演示 | 三个坏模型：缺 inertial 弹飞、collision 盒子过大卡住、轴向反 |
| 知识点 | ① inertial 至少给 mass 与对角惯性 ② collision 略小于 visual ③ 轮子关节轴 `xyz` ④ 重名 link/joint ⑤ Gazebo 标签与 URDF 的分工 |
| 跟做步骤 | 准备 bad1/bad2/bad3，学员按清单修 |
| 常见坑 | 惯性乱填（过大/为 0）爆炸；xacro 属性单位混用 |
| 预期输出 | 能独立指出并修 3 类错 |
| 小作业 | 给自己的车写"已知问题"一节 |
| 下集预告 | 模块 7：把车拉进 Gazebo |

---

## 本模块代码演进

| 集 | 对 `code/` 的改动 |
| -- | ----------------- |
| 6.3 | 新建 `src/my_car_description/`，第一版 URDF |
| 6.4 | Xacro 化、轮子宏、属性 |
| 6.5 | display.launch.py + rviz 配置 |
| 6.6 | 修正 inertial/collision；补 camera/imu |

> 配套讲义：`讲义/模块6-TF与URDF/01–06`。 
> 配套代码：`code/src/my_car_description/`。
