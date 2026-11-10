# 0.6 Python 3.12 快速上手

> 模块 0 第 6 集 
> 前置：已完成 0.5，VS Code + WSL 可用，`python3 --version` 为 3.12.x。

---

## 一、本集目标

会写**类、异常、主入口**，跑通 `MiniRobot` 小脚本，为后面 rclpy 节点打底。

学完你能独立写出：一个有属性、有方法、会抛异常、会被优雅捕获的小类。

---

## 二、效果演示

```bash
cd ~/dev/practice
python3 mini_robot.py
```

**最终现象**：

```text
[小蓝] 启动成功，电量 100.0%
[小蓝] 速度=0.50, 电量=97.5%
捕获到异常: 速度必须在 [-1, 1]，收到 1.5
[小蓝] 已停车
```

电量显示、速度校验、越界抛错、异常捕获、收尾停车——五件事一条龙。

这就是你写的第一个"面向对象"小机器人。ROS2 节点就是同样的套路：**类 + 属性 + 方法 + 入口**。

---

## 三、理论讲解

### 3.1 只用 `python3`，不用 `python`

Ubuntu 24.04 自带 **Python 3.12**，命令是 `python3`。

| 命令 | 风险 |
| ---- | ---- |
| `python3` | 正确，就是 3.12 |
| `python` | 可能不存在，或指向旧版本 |
| conda / pyenv | 本课**不用**，混用环境容易找不到包 |

**口诀**：永远敲 `python3`。

### 3.2 缩进就是语法

Python 用缩进划分代码块，**标准 4 个空格**。

```python
if a > 0:      # 冒号
    print(a)   # 4 空格，不是 Tab
```

混用 Tab 和空格，直接：

```text
IndentationError: inconsistent use of tabs and spaces in indentation
```

### 3.3 class 与 self

| 概念 | 是什么 | 比喻 |
| ---- | ------ | ---- |
| `class MiniRobot` | 类：图纸 | 机器人说明书 |
| `bot = MiniRobot(...)` | 实例：照图纸造出来的 | 一台真机器人 |
| `def __init__(self)` | 构造函数：造的时候执行 | 出厂设置 |
| `self` | "我自己"这台实例 | 机器人说"我" |
| `self.battery` | 属性 | 我的电量 |
| `def stop(self)` | 方法 | 我会停车 |

后面 ROS2 里写节点，就是 `class HelloNode(Node)`，同一个套路。

### 3.4 异常：`raise` 与 `try / except / finally`

| 关键字 | 作用 | 比喻 |
| ------ | ---- | ---- |
| `raise ValueError(...)` | 主动抛出错误 | 机器人喊"不对劲！" |
| `try:` | 试着做 | 监视机器人干活 |
| `except ValueError as e:` | 捕获某类错误 | 听到喊叫，处理 |
| `finally:` | 不管成败都做 | 收工检查 |

为什么要异常？因为**运行时错误是常态**：电量不足、速度越界、文件找不到……用 `raise` 明确报告，用 `except` 优雅兜底，程序才不会莫名其妙崩溃。

### 3.5 主入口 `if __name__ == '__main__':`

```python
if __name__ == '__main__':
    main()
```

含义：**直接运行**这个文件时才执行 `main()`；被别的文件 `import` 时不执行。

后面 ROS2 包的 `setup.py` 入口、节点的 `main()`，都依赖这个约定。

---

## 四、实操步骤（手把手）

### 步骤 0 · 打开终端

Windows Terminal → **Ubuntu**（或开始菜单 → Ubuntu）。

**预期**：提示符 `<用户名>@<电脑名>:~$`。

### 步骤 1 · 建目录并确认 Python 版本

```bash
mkdir -p ~/dev/practice
cd ~/dev/practice
python3 --version
```

> 工作目录：`~/dev/practice`

**预期**：`Python 3.12.x`。若不是，回 0.2/0.5 检查 Ubuntu 版本。

### 步骤 2 · 新建 mini_robot.py，写文件头

在 VS Code 打开：

```bash
code .
```

新建 `mini_robot.py`，先写 3 行中文注释（用途 / 内容 / 运行方式）：

```python
#!/usr/bin/env python3
# 练习：MiniRobot 类（模块0.6）
# 覆盖：类、属性、方法、异常处理
# 运行: python3 mini_robot.py
```

**预期**：文件能保存，路径是 `~/dev/practice/mini_robot.py`。

### 步骤 3 · 定义 MiniRobot 类

**为什么这么写（设计动机）**：

- 用类把"电量 / 速度 / 名字"绑在一起，比一堆全局变量干净；
- `set_speed` 里做**入参校验**，非法速度直接 `raise`，不让坏数据进来；
- 类型标注 `name: str`、`battery: float` 让接口更清楚（Python 3.12 友好）。

完整代码（与仓库 `code/m0_setup/practice_python/mini_robot.py` 一致）：

```python
#!/usr/bin/env python3
# 练习：MiniRobot 类（模块0.6）
# 覆盖：类、属性、方法、异常处理
# 运行: python3 mini_robot.py


class MiniRobot:
    """一个极简机器人：能开、能停、有电量。"""

    def __init__(self, name: str, battery: float = 100.0):
        self.name = name
        self.battery = battery
        self.speed = 0.0
        print(f'[{self.name}] 启动成功，电量 {self.battery}%')

    def set_speed(self, speed: float):
        """设置速度，范围 -1.0 ~ 1.0。"""
        if self.battery <= 0:
            raise RuntimeError('电量耗尽，无法加速')
        if speed < -1.0 or speed > 1.0:
            raise ValueError(f'速度必须在 [-1, 1]，收到 {speed}')
        self.speed = speed
        self.battery -= abs(speed) * 5
        print(f'[{self.name}] 速度={self.speed:.2f}, 电量={self.battery:.1f}%')

    def stop(self):
        self.speed = 0.0
        print(f'[{self.name}] 已停车')


def main():
    bot = MiniRobot('小蓝')
    try:
        bot.set_speed(0.5)
        bot.set_speed(1.5)  # 应触发 ValueError
    except ValueError as e:
        print('捕获到异常:', e)
    finally:
        bot.stop()


if __name__ == '__main__':
    main()
```

**预期**：文件保存成功，VS Code 无语法红线。

### 步骤 4 · 运行

```bash
cd ~/dev/practice
python3 mini_robot.py
```

**预期**：

```text
[小蓝] 启动成功，电量 100.0%
[小蓝] 速度=0.50, 电量=97.5%
捕获到异常: 速度必须在 [-1, 1]，收到 1.5
[小蓝] 已停车
```

四行都要看到。若少一行，对照代码检查 `try/except/finally`。

### 步骤 5 · 故意制造 IndentationError

把 `bot.stop()` 前面改成 **1 个 Tab**（或和周围不一致的缩进），保存后再运行：

```bash
python3 mini_robot.py
```

**预期**：看到类似

```text
IndentationError: inconsistent use of tabs and spaces in indentation
```

### 步骤 6 · 改回 4 空格

把缩进统一改回 **4 个空格**，再运行。

**预期**：恢复步骤 4 的四行输出。

> 建议 VS Code：设置 → 搜 `Tab Size` = 4，`Insert Spaces` = 勾上。

### 步骤 7 · 模块收尾：跑环境检查脚本

```bash
# 若你已把课程仓库 code/ 放到 ~/ros2_ws 或任意位置
bash ~/ros2_ws/m0_setup/check_env.sh
```

> 本模块只关心两项：**Ubuntu 24.04**、**Python 3.12**。ROS / Gazebo 项留到模块 1、7 装完再全绿。

**预期**：前两项绿色"通过"；其余项失败/警告是正常的。

---

## 五、关键 API / 命令详解

| 名称 | 作用 |
| ---- | ---- |
| `python3 --version` | 确认 3.12 |
| `python3 mini_robot.py` | 运行脚本 |
| `class MiniRobot:` | 定义类 |
| `def __init__(self, name, battery=100.0)` | 构造函数，带默认参数 |
| `self.name` / `self.battery` | 实例属性 |
| `raise ValueError(msg)` | 抛出值不合法 |
| `raise RuntimeError(msg)` | 抛出运行时故障 |
| `try / except / finally` | 监视 / 捕获 / 收尾 |
| `f'...{self.speed:.2f}...'` | f-string 格式化（保留 2 位小数） |
| `if __name__ == '__main__':` | 直接运行才执行 main |
| `check_env.sh` | 环境自检脚本 |

---

## 六、常见坑

| 报错 / 现象 | 原因 | 解法 |
| ----------- | ---- | ---- |
| `IndentationError: inconsistent use of tabs and spaces in indentation` | Tab 与空格混用 | VS Code 设 Tab=4 空格；全文件统一 |
| `python: command not found` | 用了 `python` 而不是 `python3` | 永远 `python3` |
| 以为必须上 conda / venv | 跟了别的教程 | 本课系统 Python 3.12 即可，混环境反而找不到包 |
| `SyntaxError: invalid syntax` | 中文引号 `“”` 或中文冒号 | 标点全部用英文 |
| `NameError: name 'main' is not defined` | 函数写在后面但没定义 / 拼错名 | 确认 `def main():` 存在且拼写一致 |
| 改了代码没变化 | 跑错文件 / 没保存 | 确认路径 `~/dev/practice/mini_robot.py`，`Ctrl+S` 保存 |
| `RuntimeError: 电量耗尽` 提前出现 | 电池初始值太小 | 构造时 `MiniRobot('小蓝', battery=100.0)` |

---

## 七、预期输出汇总

1. `python3 --version` 为 3.12.x；
2. `python3 mini_robot.py` 依次打印：启动 → 速度/电量 → 捕获异常 → 已停车；
3. 故意改缩进能看到 `IndentationError`，改回即恢复；
4. `check_env.sh` 里 Ubuntu 与 Python 两项通过。

---

## 八、小作业（5 分钟）

给 `MiniRobot` 加一个 `turn_left()` 方法，在 `main()` 里调用一次：

```python
def turn_left(self):
    """左转。"""
    self.battery -= 1
    print(f'[{self.name}] 左转，电量={self.battery:.1f}%')
```

运行确认输出多一行"左转"。想一想：如果电量不够，这里该 `raise` 什么？

---

## 九、下集预告

**模块 0 完成！** 进入模块 1：安装 ROS2 Jazzy，让真正的机器人软件跑起来——先搞懂"ROS 为什么长这样"。
