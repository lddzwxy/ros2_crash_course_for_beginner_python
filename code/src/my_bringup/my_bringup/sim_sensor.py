#!/usr/bin/env python3
# 模拟感知节点：定时发布模拟检测结果（感知层）
# 教学点：多节点系统中的上游发布者

import random

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimSensor(Node):
    """模拟雷达/视觉检测：随机发布障碍距离。"""

    def __init__(self):
        super().__init__('sim_sensor')
        self.declare_parameter('publish_frequency', 5.0)
        self.declare_parameter('min_distance', 0.2)

        frequency = self.get_parameter('publish_frequency').value
        # 距离下限：随机数的最小值（上限固定 3.0 m）
        self.min_distance = self.get_parameter('min_distance').value
        self.publisher_ = self.create_publisher(String, '/detection', 10)
        self.timer = self.create_timer(1.0 / max(frequency, 0.1), self.timer_callback)
        self.get_logger().info('sim_sensor 开始发布 /detection')

    def timer_callback(self):
        # 模拟障碍距离：min_distance ~ 3.0 m，下限由参数决定
        distance = round(random.uniform(self.min_distance, 3.0), 2)
        msg = String()
        msg.data = f'distance={distance}'
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SimSensor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
