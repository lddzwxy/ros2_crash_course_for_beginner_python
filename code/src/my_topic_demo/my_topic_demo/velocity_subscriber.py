#!/usr/bin/env python3
# 速度指令订阅者：订阅 /cmd_vel 并解析线速度/角速度
# 教学点：create_subscription、回调短小、日志分级

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class VelocitySubscriber(Node):
    """订阅速度指令，打印并做简单合法性检查。"""

    def __init__(self):
        super().__init__('velocity_subscriber')

        self.declare_parameter('topic_name', '/cmd_vel')
        topic_name = self.get_parameter('topic_name').value

        # 创建订阅者：类型、话题、回调、QoS 深度
        self.subscription = self.create_subscription(
            Twist, topic_name, self.listener_callback, 10)

        self.count = 0
        self.get_logger().info(f'开始订阅 {topic_name}')

    def listener_callback(self, msg: Twist):
        """收到一条速度指令就处理一次；回调要短小、不要阻塞。"""
        self.count += 1
        lin = msg.linear.x
        ang = msg.angular.z

        # 简单合法性检查：异常值用 warn
        if abs(lin) > 2.0 or abs(ang) > 2.0:
            self.get_logger().warning(
                f'速度偏大: linear.x={lin:.2f}, angular.z={ang:.2f}')

        # 每 20 条打印一次，避免刷屏
        if self.count % 20 == 1:
            self.get_logger().info(
                f'[{self.count}] 收到: linear.x={lin:.2f}, angular.z={ang:.2f}')


def main(args=None):
    rclpy.init(args=args)
    node = VelocitySubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
