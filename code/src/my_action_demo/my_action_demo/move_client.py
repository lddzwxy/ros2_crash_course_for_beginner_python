#!/usr/bin/env python3
# Action 客户端：发送前进目标、收反馈，示例中途取消
# 教学点：ActionClient、send_goal、feedback_callback、cancel_goal

import sys
import threading

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.executors import ExternalShutdownException
from rclpy.utilities import remove_ros_args

from my_interfaces.action import MoveDistance


class MoveActionClient(Node):
    """发送 /move_distance 目标并打印进度。"""

    def __init__(self):
        super().__init__('move_action_client')
        self._action_client = ActionClient(self, MoveDistance, '/move_distance')
        self._cancel_timer = None        # 保存引用以便退出前 cancel

    def send_goal(self, distance: float, cancel_after: float = 0.0):
        """发送 goal；cancel_after>0 表示 N 秒后取消。"""
        self._action_client.wait_for_server()

        goal_msg = MoveDistance.Goal()
        goal_msg.distance = float(distance)

        self.get_logger().info(f'发送目标: 前进 {distance:.2f} m')

        send_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback)
        rclpy.spin_until_future_complete(self, send_future)
        goal_handle = send_future.result()

        if not goal_handle.accepted:
            self.get_logger().error('目标被拒绝')
            return

        self.get_logger().info('目标已接受')
        result_future = goal_handle.get_result_async()

        # 定时取消（示例演示 cancel 路径）
        if cancel_after > 0:
            def _cancel():
                # 双重保险：进程已 shutdown 时绝不再碰 rclpy 对象
                if not rclpy.ok():
                    return
                self.get_logger().warning(f'{cancel_after}s 后请求取消…')
                cancel_future = goal_handle.cancel_goal_async()
                # 打印 cancel 结果
                cancel_future.add_done_callback(self._on_cancel_done)

            self._cancel_timer = threading.Timer(cancel_after, _cancel)
            self._cancel_timer.daemon = True     # 不阻塞进程退出
            self._cancel_timer.start()

        rclpy.spin_until_future_complete(self, result_future)
        result = result_future.result().result
        self.get_logger().info(
            f'结果: success={result.success}, traveled={result.distance_traveled:.2f} m')

        # 结果已拿到，取消尚未触发的定时器
        if self._cancel_timer is not None:
            self._cancel_timer.cancel()
            self._cancel_timer = None

    def feedback_callback(self, feedback_msg):
        """进度反馈回调。"""
        progress = feedback_msg.feedback.progress
        self.get_logger().info(f'反馈进度: {progress*100:.0f}%')

    def _on_cancel_done(self, future):
        """打印 cancel_goal_async 的返回结果。"""
        try:
            response = future.result()
        except Exception as e:
            self.get_logger().error(f'取消请求失败: {e}')
            return
        if response is None or not response.goals_canceling:
            self.get_logger().info('取消请求被忽略（目标可能已结束）')
        else:
            self.get_logger().info('取消请求已被接受')


def main(args=None):
    rclpy.init(args=args)

    distance = 5.0
    cancel_after = 0.0
    # 用法: ros2 run my_action_demo move_client [distance] [cancel_after_sec]
    # remove_ros_args 剔除 --ros-args 部分，避免把 ROS 参数当成业务参数
    argv = remove_ros_args(args=sys.argv)
    if len(argv) > 1:
        distance = float(argv[1])
    if len(argv) > 2:
        cancel_after = float(argv[2])

    node = MoveActionClient()
    try:
        node.send_goal(distance, cancel_after)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        # 兜底取消定时器，防止 send_goal 内异常时泄漏
        if node._cancel_timer is not None:
            node._cancel_timer.cancel()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
