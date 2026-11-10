#!/usr/bin/env python3
# 参数演示节点：声明/读取参数，支持 ros2 param set 动态改频率
# 教学点：declare_parameter、参数变更回调、create_timer

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult
from std_msgs.msg import String


class ParamNode(Node):
    """按参数频率发布心跳字符串。"""

    def __init__(self):
        super().__init__('param_node')

        # 声明参数：名称、默认值、描述（可选）
        self.declare_parameter('publish_frequency', 10.0)
        self.declare_parameter('topic_name', '/heartbeat')

        self._frequency = self.get_parameter('publish_frequency').value
        self.publisher_ = self.create_publisher(
            String, self.get_parameter('topic_name').value, 10)
        self._rebuild_timer()

        # 参数变更回调：ros2 param set 会先进这里，可安全地重建定时器
        self.add_on_set_parameters_callback(self._on_params_set)

        self.get_logger().info('param_node 已启动，可用 ros2 param set 修改频率')

    def _rebuild_timer(self):
        """按当前频率重建定时器。

        注意：不要在定时器回调里销毁/重建自己所在的定时器（危险操作），
        所以重建动作统一放到参数回调里触发。
        """
        period = 1.0 / max(self._frequency, 0.1)
        if hasattr(self, 'timer'):
            self.destroy_timer(self.timer)
        self.timer = self.create_timer(period, self.timer_callback)

    def _on_params_set(self, params):
        """参数生效前的回调：感知频率变更并重建定时器。"""
        for p in params:
            if p.name == 'publish_frequency':
                new_freq = float(p.value)
                if abs(new_freq - self._frequency) > 1e-6:
                    self.get_logger().info(
                        f'检测到频率变更: {self._frequency} -> {new_freq}')
                    self._frequency = new_freq
                    self._rebuild_timer()
        return SetParametersResult(successful=True)

    def timer_callback(self):
        msg = String()
        msg.data = f'heartbeat @ {self._frequency:.2f} Hz'
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ParamNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
