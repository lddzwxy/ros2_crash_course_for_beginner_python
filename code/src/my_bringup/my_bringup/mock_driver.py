#!/usr/bin/env python3
# 模拟驱动节点：订阅 /cmd_vel 并打印执行动作（执行层）
# 教学点：订阅者作执行器；回调不要阻塞

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class MockDriver(Node):
    """打印收到的速度指令，模拟底层驱动。"""

    def __init__(self):
        super().__init__('mock_driver')
        self.sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_callback, 10)
        self.count = 0
        self.get_logger().info('mock_driver 等待 /cmd_vel …')

    def cmd_callback(self, msg: Twist):
        self.count += 1
        if self.count % 10 == 1:
            self.get_logger().info(
                f'执行: linear.x={msg.linear.x:.2f}, angular.z={msg.angular.z:.2f}')


def main(args=None):
    rclpy.init(args=args)
    node = MockDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
