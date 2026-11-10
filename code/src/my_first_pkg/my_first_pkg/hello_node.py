#!/usr/bin/env python3
# 第一个 ROS2 节点：向终端打印问候，并发布一条简单日志
# 教学点：继承 Node、构造节点名、日志、spin、main 入口

import rclpy
from rclpy.node import Node


class HelloNode(Node):
    """最小 ROS2 节点：启动即打印 Hello ROS2。"""

    def __init__(self):
        # 节点名 hello_node；可被 --ros-args -r __node:=xxx 覆盖
        super().__init__('hello_node')
        self.get_logger().info('Hello ROS2')
        self.get_logger().info('欢迎来到 Jazzy + Python 3.12 之旅')


def main(args=None):
    # 1) 初始化 rclpy 上下文（每个进程一次）
    rclpy.init(args=args)
    # 2) 创建节点实例
    node = HelloNode()
    try:
        # 3) spin：进入事件循环，处理回调（本例无定时器，Ctrl+C 退出）
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # 4) 释放资源
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
