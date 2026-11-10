# 模块 4 · 参数、Launch、Lifecycle 与工程化（细纲 · 5 集）

> 目标：会声明/读取/动态改参数，会用 Launch 组织多节点，项目结构收干净。 
> 前置：模块 2–3 已有 pub/sub 与 service/action。 
> 产出包：`my_bringup`（ament_python，含参数节点、demo 系统、launch、YAML、lifecycle 了解）。

---

## 4.1 参数 Parameter

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 声明、读取、动态修改参数；会写 YAML |
| 开场演示 | `ros2 param set` 改频率，发布节奏立刻变化 |
| 知识点 | ① declare_parameter 默认值与描述 ② get/set ③ 只读 vs 可动态改 ④ 参数类型 ⑤ YAML 结构与 node 名对应 |
| 跟做步骤 | **1** 在 `my_bringup/param_node.py` 中 `declare_parameter('publish_frequency', 10.0)`<br>**2** 启动后 `ros2 param list /param_node`<br>**3** `ros2 param get /param_node publish_frequency`<br>**4** `ros2 param set /param_node publish_frequency 2.0`，观察日志频率变化<br>**5** `ros2 param dump /param_node --output-dir ~/ros2_ws/src/my_bringup/config`<br>**6** 写 `config/params.yaml`：`param_node: ros__parameters: publish_frequency: 10.0` |
| 关键 API | `declare_parameter`、`get_parameter`、`add_on_set_parameters_callback`（可选） |
| 常见坑 | 声明名与读取名不一致；没 declare 直接 get（Jazzy 严格）；YAML 里 node 名和实际节点名不一致 |
| 预期输出 | set 后频率明显变化；YAML 可 dump/load |
| 小作业 | 增加参数 `topic_name`，set 后发布话题改变（或启动时生效） |
| 下集预告 | 参数会了，怎么一键启动多个节点？ |

---

## 4.2 Launch 一键多节点

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 写 Python launch：多节点、remap、加载 YAML、namespace |
| 开场演示 | `ros2 launch my_bringup demo_system.launch.py` 一次起 3 节点 |
| 知识点 | ① `launch.LaunchDescription` + `Node(...)` ② `parameters=[yaml]` ③ `remappings` ④ `namespace` ⑤ data_files 安装 launch/config 到 share |
| 跟做步骤 | **1** 写 `launch/demo_system.launch.py`：Node(package/executable/name/parameters/remappings)<br>**2** setup.py `data_files` 加 `glob('launch/*.launch.py')` 与 `glob('config/*.yaml')` 到 share<br>**3** colcon build --packages-select my_bringup<br>**4** source 后 `ros2 launch my_bringup demo_system.launch.py`<br>**5** `ros2 node list` 确认全起来了 |
| 关键 API | `launch_ros.actions.Node`、`IncludeLaunchDescription`（可选） |
| 常见坑 | launch 没进 share（`ros2 launch` 找不到）；路径写死绝对路径；parameters 写成字符串字典格式错 |
| 预期输出 | 一条命令起多节点；参数从 YAML 生效 |
| 小作业 | 加一个 remapping 把某话题改名并验证 |
| 下集预告 | 用多节点搭一条最小软件栈 |

---

## 4.3 多节点小系统串联

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 感知→决策→执行 三节点用话题串起来，统一命名空间 |
| 开场演示 | rqt_graph 显示三节点链路 |
| 知识点 | ① 分层：sensor/decision/driver ② 话题契约 ③ 命名空间避免冲突 ④ 用 launch 起整栈 |
| 跟做步骤 | **1** `sim_sensor.py`：模拟检测，发布 `/detection`（std_msgs/String 或自定义）<br>**2** `decision_node.py`：订阅检测，发布 `/cmd_vel` 或 `/command`<br>**3** `mock_driver.py`：订阅指令，日志"执行"<br>**4** launch 用 `namespace='robot1'` 启动全套<br>**5** rqt_graph / `ros2 topic echo` 验证链路 |
| 常见坑 | 无统一命名空间导致话题全局污染；消息类型不一致连不上 |
| 预期输出 | 图上能画出 sensor→decision→driver |
| 小作业 | 在 decision 中加"距离小于阈值则停"逻辑 |
| 下集预告 | Lifecycle：节点的开机流程（了解） |

---

## 4.4 Lifecycle（了解为主）

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 看懂状态机，会 configure/activate；不深挖 |
| 开场演示 | `ros2 lifecycle set /lc_node configure` / `activate` 前后节点行为变化 |
| 知识点 | ① unconfigured→inactive→active→finalized ② configure/activate/deactivate/cleanup ③ 未 activate 不发数据 ④ 何时需要：硬件启动、模式切换 |
| 跟做步骤 | **1** 运行 `lifecycle_demo.py`<br>**2** `ros2 lifecycle list /lc_node`<br>**3** set configure → activate<br>**4** 观察才开始 publish |
| 常见坑 | 状态没 activate 就以为节点坏了 |
| 预期输出 | 能说出生命周期四步 |
| 小作业 | 把 lifecycle 节点 deactivate，看数据是否停止 |
| 下集预告 | 项目结构与代码规范 |

---

## 4.5 项目结构与代码规范

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 工程收干净：目录、README、rosdep、依赖进 package.xml |
| 开场演示 | 一个干净的 my_bringup 树 + README 版本卡 |
| 知识点 | ① 依赖写 package.xml 而不是靠记忆 ② `rosdep install --from-paths src -y` ③ README：版本卡、启动方式、节点表 ④ lint：`ament_flake8`/`ament_pep257`（可选） |
| 跟做步骤 | **1** 检查每个包 package.xml 依赖是否完整<br>**2** `rosdep install --from-paths src -y --ignore-src`<br>**3** 写 my_bringup/README.md 模板 |
| 常见坑 | 依赖靠"反正我机器上有"；换机就挂 |
| 预期输出 | 新机器按 README 能复现启动 |
| 小作业 | 给 my_topic_demo 补全 README 版本卡 |
| 下集预告 | 模块 5：可视化与调试工具 |

---

## 本模块代码演进

| 集 | 对 `code/` 的改动 |
| -- | ----------------- |
| 4.1 | 新建 `src/my_bringup/`，`param_node.py`，`config/params.yaml` |
| 4.2 | `launch/demo_system.launch.py` + setup.py data_files |
| 4.3 | `sim_sensor.py`、`decision_node.py`、`mock_driver.py` |
| 4.4 | `lifecycle_demo.py` |
| 4.5 | README、依赖检查 |

> 配套讲义：`讲义/模块4-参数与Launch/01–05`。 
> 配套代码：`code/src/my_bringup/`。
