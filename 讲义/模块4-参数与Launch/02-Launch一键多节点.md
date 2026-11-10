# 4.2 Launch 一键多节点

> 模块 4 第 2 集 
> 前置：已完成 4.1，`my_bringup` 包与 `param_node` 可运行；`config/params.yaml` 已就绪。

---

## 一、本集目标

用 **Python launch 文件**把多个节点、参数 YAML、话题改名**一键拉起**，完成：

`写 launch → data_files 装进 share → colcon build → ros2 launch` 闭环。

记住本模块最硬的一条规则：**launch / config 不装进 share，`ros2 launch` 就找不到**。

---

## 二、效果演示

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch my_bringup demo_system.launch.py
```

**预期**：一条命令，终端里交错出现 4 个节点的日志（sim_sensor / decision_node / mock_driver / param_node），不用开 4 个终端。

再开一个终端：

```bash
ros2 node list
```

**预期**：同时看到

```text
/decision_node
/mock_driver
/param_node
/sim_sensor
```

---

## 三、理论讲解

### 3.1 为什么需要 launch？

手工开 4 个终端、source 4 次、敲 4 条 `ros2 run`——机器人一多就崩。 
**launch** 就是"开机剧本"：谁先起、带什么参数、话题怎么接，写在一个文件里，一条命令开整场。

比喻：`ros2 run` 是手点一盏灯；`ros2 launch` 是墙上的**总开关**。

### 3.2 launch 文件长什么样

Jazzy 用 **Python launch**（不是 XML、不是 YAML）：

```text
generate_launch_description()
  └── LaunchDescription([ Node(...), Node(...), ... ])
```

每个 `Node(...)` 对应一条 `ros2 run`：

| 字段 | 对应 ros2 run 的哪部分 |
| ---- | ---------------------- |
| `package='my_bringup'` | 包名 |
| `executable='param_node'` | 可执行名 |
| `name='param_node'` | 节点名（可覆盖） |
| `parameters=[params_file]` | `--params-file` |
| `remappings=[('/a','/b')]` | `--ros-args -r /a:=/b` |
| `namespace='robot1'` | 把节点塞进命名空间 |
| `output='screen'` | 日志打到终端 |

### 3.3 data_files：launch 的"安装许可证"

Python 包默认只装 `.py`。launch 和 YAML 是**数据文件**，必须在 `setup.py` 的 `data_files` 里显式登记：

```text
share/my_bringup/launch/*.launch.py
share/my_bringup/config/*.yaml
```

装进 share 后，`ros2 launch` 才能通过 ament 索引找到包、再找到 launch 文件。 
**这一步漏了，是最常见的"文件明明在却找不到"**。

### 3.4 路径不要写死

YAML 路径用 `FindPackageShare` + `PathJoinSubstitution` 动态找包：

```python
params_file = PathJoinSubstitution([
    FindPackageShare('my_bringup'), 'config', 'params.yaml'])
```

好处：换机器、换安装前缀都不用改代码。

---

## 四、实操步骤（手把手）

> 仓库对照：`code/src/my_bringup/launch/demo_system.launch.py` 与 `setup.py`。 

### 步骤 0 · 打开终端并进入包目录

Windows Terminal → Ubuntu：

```bash
cd ~/ros2_ws/src/my_bringup
mkdir -p launch
```

**预期**：`ls` 能看到 `my_bringup/  config/  launch/  package.xml  setup.py ...`。

### 步骤 1 · 写 demo_system.launch.py

**为什么这么写**：

- 用 `generate_launch_description()` 约定入口，launch 系统自动调用；
- 每个 `Node` 写清 `package/executable/name`，和 `ros2 run` 一一对应；
- 参数用 YAML 注入，不在 launch 里硬编码数字；
- `output='screen'` 让日志直接进终端，方便教学观察。

完整代码（教学分步版，完整版见仓库）：

```python
# ~/ros2_ws/src/my_bringup/launch/demo_system.launch.py
# 一键启动多节点小系统：感知 → 决策 → 执行
# 用法: ros2 launch my_bringup demo_system.launch.py

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params_file = PathJoinSubstitution([
        FindPackageShare('my_bringup'), 'config', 'params.yaml'])

    return LaunchDescription([
        # 参数心跳演示
        Node(
            package='my_bringup',
            executable='param_node',
            name='param_node',
            output='screen',
            parameters=[params_file],
        ),
        # 乌龟节点
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtle',
            output='screen',
            # 可在此 remap 话题
            # remappings=[('/turtle1/cmd_vel', '/robot1/cmd_vel')],
        ),
        # # 感知层
        # Node(
        #     package='my_bringup',
        #     executable='sim_sensor',
        #     name='sim_sensor',
        #     output='screen',
        #     parameters=[params_file],
        # ),
        # # 决策层
        # Node(
        #     package='my_bringup',
        #     executable='decision_node',
        #     name='decision_node',
        #     output='screen',
        #     parameters=[params_file],
        # ),
        # # 执行层
        # Node(
        #     package='my_bringup',
        #     executable='mock_driver',
        #     name='mock_driver',
        #     output='screen',
        # ),
    ])
```

> 本集先保证 launch 机制跑通。`sim_sensor` 等节点下一集（4.3）细讲；现在若可执行文件还不存在，可先只保留 `param_node` 那一段，其余注释掉，编译运行通过后再补齐。

**预期**：Python 语法无红线；函数名必须是 `generate_launch_description`。

### 步骤 2 · setup.py：把 launch / config 装进 share（关键！）

打开 `~/ros2_ws/src/my_bringup/setup.py`，在 `data_files` 里加入两行安装规则：

```python
# ~/ros2_ws/src/my_bringup/setup.py 片段
from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'my_bringup'

setup(
    name=package_name,
    # ... 其余字段同 4.1 ...
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 把 launch / config 装进 share，ros2 launch 才能发现
        (os.path.join('share', package_name, 'launch'),
         glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'),
         glob('config/*.yaml')),
    ],
    entry_points={
        'console_scripts': [
            'param_node = my_bringup.param_node:main',
            # 'sim_sensor = my_bringup.sim_sensor:main',
            # 'decision_node = my_bringup.decision_node:main',
            # 'mock_driver = my_bringup.mock_driver:main',
            # 'lifecycle_demo = my_bringup.lifecycle_demo:main',
        ],
    },
)
```

含义：

- `glob('launch/*.launch.py')` 把 launch 目录下所有 launch 文件装到 `share/my_bringup/launch/`；
- `glob('config/*.yaml')` 把 YAML 装到 `share/my_bringup/config/`；
- 少写这两行，`ros2 launch` 会报 `file not found`。

**预期**：`data_files` 里有 `launch` 和 `config` 两条 `os.path.join(...)`。

### 步骤 3 · 编译

```bash
cd ~/ros2_ws
colcon build --packages-select my_bringup --symlink-install
```

**预期**：`Summary: 1 package finished`。

验证安装结果：

```bash
ls ~/ros2_ws/install/my_bringup/share/my_bringup/launch/
ls ~/ros2_ws/install/my_bringup/share/my_bringup/config/
```

**预期**：分别看到 `demo_system.launch.py` 和 `params.yaml`。 
（`--symlink-install` 下可能是符号链接，内容仍指向 src。）

### 步骤 4 · source 并确认 launch 可被发现

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch my_bringup demo_system.launch.py --show-args
```

**预期**：打印 launch 文件路径与可用参数（可为空），**不报 file not found**。

### 步骤 5 · 一键启动

```bash
ros2 launch my_bringup demo_system.launch.py
```

**预期**：终端交错输出多节点日志，例如：

```text
[INFO] [turtle]: Starting turtlesim with node name /turtle
[INFO] [param_node]: param_node 已启动，可用 ros2 param set 修改频率
```

按 `Ctrl+C`，全部节点一起退出。

### 步骤 6 · 验证节点都在

启动后另开终端：

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 node list
ros2 param get /param_node publish_frequency
```

**预期**：`ros2 node list` 看到 2 个节点；`publish_frequency` 为 **5.0**（来自 YAML，不是代码默认 10.0）。

### 步骤 7 · 试 remap（话题改名）

把 `demo_system.launch.py` 里 turtlesim_node 的注释行打开：

```python
remappings=[('/cmd_vel', '/robot1/cmd_vel')],
```

重新编译（launch 是数据文件，symlink 下一般也要确认安装）并启动，再看：

```bash
ros2 topic list
```

**预期**：出现 `/robot1/cmd_vel` 而不是（或不仅是）`/cmd_vel`。

---

## 五、关键 API / 命令详解

| 名称 | 作用 |
| ---- | ---- |
| `generate_launch_description()` | launch 文件约定入口，返回 `LaunchDescription` |
| `LaunchDescription([...])` | 启动动作列表 |
| `launch_ros.actions.Node` | 对应一个 `ros2 run` |
| `parameters=[yaml_path]` | 给节点注入 YAML 参数 |
| `remappings=[(from, to)]` | 话题重映射 |
| `namespace='xxx'` | 节点与话题进入命名空间 |
| `FindPackageShare('pkg')` | 动态找包的 share 目录 |
| `PathJoinSubstitution([...])` | 跨平台拼路径 |
| `data_files` + `glob` | 把 launch/config 装进 share |
| `ros2 launch <pkg> <file>` | 按 launch 剧本启动 |
| `ros2 launch ... --show-args` | 查看 launch 可传参数 |

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| `Package 'my_bringup' not found` / `file not found` | launch 没装进 share 或没 source | setup.py 加 data_files，重 build，source 两层 |
| `ros2 launch` 列不出 launch 文件 | `glob('launch/*.launch.py')` 模式不匹配 | 文件名必须以 `.launch.py` 结尾 |
| `generate_launch_description` 缺失/写错名 | 函数名拼错 | 必须一字不差 |
| YAML 路径写死 `/home/xxx/...` | 换机失效 | 用 `FindPackageShare` |
| `parameters` 传成 `[{'publish_frequency': 5}]` 格式错 | 字典/列表写法混淆 | 教学统一传 YAML 路径字符串/Substitution |
| 改了 launch 行为没变 | 没重新 build / 没重启 launch | 重 `colcon build` 后重新 `ros2 launch` |
| 节点日志看不到 | 没写 `output='screen'` | Node 加 `output='screen'` |

---

## 七、预期输出汇总

1. `install/my_bringup/share/my_bringup/launch/` 下有 `demo_system.launch.py`；
2. `ros2 launch my_bringup demo_system.launch.py` 一键起多节点；
3. `ros2 node list` 能看到全部节点；
4. `/param_node publish_frequency` 读到 YAML 里的 **5.0**；
5. remap 后话题名发生变化。

---

## 八、小作业（5 分钟）

1. 在 launch 里把 `param_node` 的 `name='param_node'` 改成 `name='heartbeat_node'`，启动后用 `ros2 node list` 观察（注意 YAML 顶层键也要跟着改，否则参数不生效）；
2. 给 `mock_driver` 加 `namespace='robot1'`，用 `ros2 node list` / `ros2 topic list` 看它去了哪；
3. 把 `output='screen'` 删掉再启动，体会日志去哪了。

---

## 九、下集预告

总开关装好了。下一集把 **感知 → 决策 → 执行** 三个节点真正串成一条数据流：**4.3 多节点小系统串联**。
