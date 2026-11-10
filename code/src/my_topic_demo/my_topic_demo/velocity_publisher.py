#!/usr/bin/env python3
# 速度指令发布者：按频率发布 geometry_msgs/Twist 到 /cmd_vel
# 教学点：create_publisher、create_timer、declare_parameter、spin

import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class VelocityPublisher(Node):
    """定时发布速度指令，模拟遥控或自动控制。"""

    def __init__(self):
        super().__init__('velocity_publisher')

        # 声明参数：发布频率（Hz）与目标话题名
        self.declare_parameter('publish_frequency', 10.0)
        self.declare_parameter('topic_name', '/cmd_vel')

        frequency = self.get_parameter('publish_frequency').value
        topic_name = self.get_parameter('topic_name').value

        # 创建发布者：类型、话题、QoS 队列深度
        self.publisher_ = self.create_publisher(Twist, topic_name, 10)

        # 定时器驱动发布，保证频率稳定（比 while+sleep 更规范）
        # 频率做下限保护，防止 0/负数导致除零
        timer_period = 1.0 / max(frequency, 0.1)
        self.timer_period = timer_period
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.elapsed = 0.0
        self.tick = 0

        self.get_logger().info(
            f'开始发布速度到 {topic_name}，频率 {frequency} Hz')

    def timer_callback(self):
        """每隔 timer_period 发一条速度指令。"""
        msg = Twist()
        # 线速度在 0.05~0.25 之间缓慢变化，便于观察
        msg.linear.x = 0.15 + 0.1 * math.sin(self.elapsed * 0.5)
        # 角速度正弦摆动：车会左右画弧
        msg.angular.z = 0.3 * math.sin(self.elapsed * 0.3)

        self.publisher_.publish(msg)
        # 按真实经过时间累加（与 publish_frequency 联动），波形快慢才正确
        self.elapsed += self.timer_period
        self.tick += 1

        # 日志节流：避免刷屏（每 20 次打一条）
        if self.tick % 20 == 0:
            self.get_logger().info(
                f'发速度: linear.x={msg.linear.x:.2f}, angular.z={msg.angular.z:.2f}')


def main(args=None):
    rclpy.init(args=args)
    node = VelocityPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
