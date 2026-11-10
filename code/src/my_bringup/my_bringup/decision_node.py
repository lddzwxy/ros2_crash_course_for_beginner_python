#!/usr/bin/env python3
# 决策节点：订阅检测，根据距离决定前进/停止（决策层）
# 教学点：订阅-发布链路中的中间节点

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist


class DecisionNode(Node):
    """距离小于阈值则停车，否则前进。"""

    def __init__(self):
        super().__init__('decision_node')
        self.declare_parameter('stop_distance', 0.5)

        self.stop_distance = self.get_parameter('stop_distance').value
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub = self.create_subscription(
            String, '/detection', self.detection_callback, 10)

        self.get_logger().info(
            f'decision_node 就绪，停车阈值 {self.stop_distance} m')

    def detection_callback(self, msg: String):
        # 消息形如 "distance=1.23"
        try:
            distance = float(msg.data.split('=')[1])
        except (IndexError, ValueError):
            self.get_logger().warning(f'无法解析检测消息: {msg.data!r}')
            return

        cmd = Twist()
        if distance < self.stop_distance:
            # 障碍过近：停车
            cmd.linear.x = 0.0
            self.get_logger().warning(f'障碍过近 ({distance:.2f} m)，停车')
        else:
            cmd.linear.x = 0.2
        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = DecisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
