#!/usr/bin/env python3
# Lifecycle 演示节点（了解）：configure/activate 后才开始发布
# 教学点：生命周期状态机；未 activate 不发数据

import rclpy
from rclpy.lifecycle import Node as LifecycleNode, State, TransitionCallbackReturn
from std_msgs.msg import String


class LifecycleDemo(LifecycleNode):
    """最小 Lifecycle 节点：on_configure 开资源，on_activate 开定时器。"""

    def __init__(self):
        super().__init__('lifecycle_demo')
        self.publisher_ = None
        self.timer = None
        self.get_logger().info('lifecycle_demo 创建（unconfigured）')

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        self.publisher_ = self.create_lifecycle_publisher(String, '/lc_heartbeat', 10)
        self.get_logger().info('已 configure：publisher 就绪')
        # super() 会把迁移转发给托管实体（lifecycle publisher），必须调用
        return super().on_configure(state)

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        # 激活后才启动定时器
        self.timer = self.create_timer(1.0, self._on_timer)
        self.get_logger().info('已 activate：开始发布')
        # 必须调用 super()：它激活 lifecycle publisher，
        # 否则 publish() 会被 @when_enabled 拦下，消息静默丢弃
        return super().on_activate(state)

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        if self.timer:
            self.destroy_timer(self.timer)
            self.timer = None
        self.get_logger().info('已 deactivate：停止发布')
        return super().on_deactivate(state)

    def on_cleanup(self, state: State) -> TransitionCallbackReturn:
        if self.publisher_:
            self.destroy_publisher(self.publisher_)
            self.publisher_ = None
        self.get_logger().info('已 cleanup')
        return super().on_cleanup(state)

    def _on_timer(self):
        msg = String()
        msg.data = 'lc heartbeat'
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = LifecycleDemo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
