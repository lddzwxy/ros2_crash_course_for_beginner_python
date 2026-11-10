# 模块 1 · ROS2 初印象：从安装到第一次编译（细纲 · 5 集）

> 目标：把学员从"会用 Ubuntu"带到"拥有第一个可 `ros2 run` 的 ROS2 包"。 
> 前置：模块 0 已完成（WSL2 + Ubuntu 24.04 + VS Code + Python 3.12）。 
> 产出包：`my_first_pkg`（ament_python）。 
> 版本钉死：ROS2 **Jazzy Jalisco** · apt 前缀 `ros-jazzy-*` · 构建 `colcon`。

---

## 1.1 ROS 为什么长这样

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 理解 ROS2 解决什么问题：进程间通信 + 工具 + 生态 |
| 开场演示 | 一张图：两个陌生节点通过 Topic 说话（不写代码，只画/放动画） |
| 知识点 | ① 机器人软件为什么要解耦 ② ROS2=通信中间件+工具+库 ③ 节点/话题/服务/动作/参数 五件套直觉 ④ 不是实时操作系统 |
| 跟做步骤 | 无需终端；对照"广播=Topic / 打电话=Service / 点外卖=Action"表讲 |
| 关键概念 | Node、Topic、Service、Action、Parameter、Package、Workspace |
| 常见坑 | 把 ROS2 当成一个装完就有界面的软件；以为 ROS2 = 实时系统 |
| 预期输出 | 学员能口头说出三种通信方式的生活比喻 |
| 小作业 | 用自己的话写 3 句话：ROS2 是什么 / 不是什么 / 本课要做出什么 |
| 下集预告 | 下集把 ROS2 真正装进 Ubuntu |

---

## 1.2 安装 ROS2 Jazzy

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 装好 `ros-jazzy-desktop`，`ros2 doctor` 无致命错误，source 写入 bashrc |
| 开场演示 | 新终端直接敲 `ros2 --help` 有输出 |
| 知识点 | ① locale 配置 ② 添加 ROS2 Jazzy apt 源（Ubuntu 24.04 / noble）③ `ros-jazzy-desktop` ④ rosdep 初始化 ⑤ source 到 `.bashrc` |
| 跟做步骤 | **1** 更新软件包索引：`sudo apt update && sudo apt upgrade -y`<br>**2** 安装基础工具：`sudo apt install -y software-properties-common curl gnupg lsb-release`<br>**3** 设置 locale（UTF-8）：`sudo apt install -y locales && sudo locale-gen en_US en_US.UTF-8 && sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8`，重开终端<br>**4** 添加 ROS2 apt 源（Jazzy，按官方 Jazzy 文档命令；启用 universe 仓库）<br>**5** `sudo apt update`<br>**6** 安装：`sudo apt install -y ros-jazzy-desktop python3-colcon-common-extensions python3-rosdep python3-vcstool python3-argcomplete`<br>**7** 写入 bashrc：`echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc && source ~/.bashrc`<br>**8** rosdep：`sudo rosdep init && rosdep update`<br>**9** 验证：`ros2 doctor`、`printenv ROS_DISTRO`（应为 `jazzy`）、`python3 --version`（3.12.x） |
| 关键命令 | `sudo apt install ros-jazzy-desktop`、`ros2 doctor`、`source /opt/ros/jazzy/setup.bash` |
| 常见坑 | ① 忘记 source，`ros2: command not found` → 写 bashrc 或手动 source<br>② 装成 Humble（看文档没切到 Jazzy）→ `printenv ROS_DISTRO` 必须是 `jazzy`<br>③ 源与 24.04 不匹配导致 404 → 确认源里是 `noble` |
| 预期输出 | `ros2 doctor` 显示系统状态；`ROS_DISTRO=jazzy`；`python3` 是 3.12 |
| 小作业 | 故意开一个**不** source 的终端，观察 `ros2` 不存在；再 source 后恢复正常 |
| 下集预告 | 装好了，下集用 turtlesim 真正发号施令 |

---

## 1.3 turtlesim 与 ros2 CLI

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 会用 `ros2 run/node/topic/param` 核心命令观察并控制 turtlesim |
| 开场演示 | 三个终端：乌龟画圆 + `ros2 topic echo` 看到速度指令 |
| 知识点 | ① `ros2 run` 启动可执行 ② `ros2 node list` ③ `ros2 topic list/echo/hz` ④ `ros2 param list` ⑤ 可执行 ≠ 节点名 |
| 跟做步骤 | **1** 终端A：`ros2 run turtlesim turtlesim_node`<br>**2** 终端B：`ros2 run turtlesim turtle_teleop_key`<br>**3** 终端C：`ros2 node list`、`ros2 topic list`、`ros2 topic echo /turtle1/cmd_vel`<br>**4** `ros2 topic hz /turtle1/cmd_vel`、`ros2 topic info /turtle1/cmd_vel`<br>**5** `ros2 param list /turtlesim` |
| 关键命令 | `ros2 run`、`ros2 node list`、`ros2 topic list/echo/hz/info`、`ros2 param list` |
| 常见坑 | ① 只抄命令不理解：要能说出"谁是 publisher / subscriber"<br>② 终端被 teleop 占用导致无法继续敲命令 → 多开终端<br>③ 包名写错：`turtlesim` 是包，`turtlesim_node` 是可执行 |
| 预期输出 | 乌龟随键盘移动；`echo` 能打印 `linear.x`；`node list` 至少两个节点 |
| 小作业 | 不查笔记，写出命令：查看 `/turtle1/cmd_vel` 的消息类型和频率 |
| 下集预告 | 会用别人的节点了，下集自己建包 |

---

## 1.4 工作空间与包

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | 搞清 `ros2_ws` 目录约定，用 `ros2 pkg create` 生成 `my_first_pkg` |
| 开场演示 | `tree` 显示 my_first_pkg 结构，指出每个文件干什么 |
| 知识点 | ① 工作空间 `src/` / `build/` / `install/` / `log/` ② 包=最小交付单元 ③ `ament_python` vs `ament_cmake` ④ `package.xml` / `setup.py` / `setup.cfg` / `resource/` ⑤ 包名规则：小写+下划线 |
| 跟做步骤 | **1** `mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src`<br>**2** `ros2 pkg create --build-type ament_python --node-name hello_node my_first_pkg`<br>**3** 查看生成结构：`tree my_first_pkg` 或 `find my_first_pkg -type f`<br>**4** 对照讲解 package.xml 依赖、setup.py entry_points、setup.cfg |
| 关键命令 | `ros2 pkg create --build-type ament_python --node-name hello_node my_first_pkg` |
| 关键文件 | `package.xml`（元数据+依赖）、`setup.py`（安装与入口）、`setup.cfg`（script-dir/data-files）、`resource/my_first_pkg`（marker） |
| 常见坑 | ① 在 `~/ros2_ws` 根下建包而不是 `src/`<br>② 包名用了大写或横线（非法）<br>③ 漏 `resource/` 导致包不可见 |
| 预期输出 | `my_first_pkg` 目录存在，含 `package.xml` `setup.py` `my_first_pkg/hello_node.py` |
| 小作业 | 在 package.xml 里找出"这个包叫什么、依赖什么"两行并写到笔记 |
| 下集预告 | 下集 colcon 编译，让 Hello 真正跑起来 |

---

## 1.5 colcon 编译与排查

| 字段 | 内容 |
| ---- | ---- |
| 本集目标 | `colcon build` → `source install` → `ros2 run my_first_pkg hello_node` 全闭环 |
| 开场演示 | 终端打印 `Hello ROS2`；再开终端同样能跑 |
| 知识点 | ① colcon 工作空间构建 ② `--symlink-install` 含义 ③ source `install/setup.bash` ④ `ros2 pkg executables` / `ros2 run` ⑤ 编译失败看 `log/` |
| 跟做步骤 | **1** 编辑 `hello_node.py`：继承 Node，构造里 `super().__init__('hello_node')`，`self.get_logger().info('Hello ROS2')`，加 `main()` + `rclpy.init/spin/shutdown`<br>**2** 确认 `setup.py` 的 `entry_points` 含 `hello_node = my_first_pkg.hello_node:main`<br>**3** `cd ~/ros2_ws && colcon build --symlink-install`<br>**4** `source install/setup.bash`（或 source 两层：先 `/opt/ros/jazzy` 再 `install`）<br>**5** `ros2 pkg executables my_first_pkg`<br>**6** `ros2 run my_first_pkg hello_node` |
| 关键命令 | `colcon build --symlink-install`、`source install/setup.bash`、`ros2 run my_first_pkg hello_node` |
| 常见坑 | ① **未 source install**：`Package 'my_first_pkg' not found`<br>② entry_points 与文件名不一致<br>③ 缩进/语法错误导致编译失败 → 看终端报错行号<br>④ 修改 .py 后未重新 build（非 symlink）或未新开终端 |
| 预期输出 | 编译 `Finished`；运行打印 Hello；`ros2 node list` 可看到 `/hello_node` |
| 小作业 | 改字符串为自己的名字，用 `--symlink-install` 是否需要重新 build？验证并记录 |
| 下集预告 | 进入模块 2：节点与话题通信 |

---

## 本模块代码演进

| 集 | 对 `code/` 的改动 |
| -- | ----------------- |
| 1.4 | 新建 `src/my_first_pkg/`（ros2 pkg create 结果） |
| 1.5 | 补全 `hello_node.py`；核对 `package.xml` / `setup.py` / `setup.cfg` |

> 配套讲义：`讲义/模块1-ROS2初印象/01–05`。 
> 配套代码：`code/src/my_first_pkg/`。
