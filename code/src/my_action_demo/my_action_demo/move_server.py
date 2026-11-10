#!/usr/bin/env python3
# Action 服务端：模拟"前进 N 米"，带进度反馈，支持取消
# 教学点：ActionServer、execute 回调、publish_feedback、取消处理

import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.executors import MultiThreadedExecutor, ExternalShutdownException

from my_interfaces.action import MoveDistance


class MoveActionServer(Node):
    """按速度参数模拟里程累加，达成目标距离后返回结果。"""

    def __init__(self):
        super().__init__('move_action_server')

        self.declare_parameter('speed_mps', 0.2)
        self.speed = self.get_parameter('speed_mps').value
        # 校验 speed，避免 step=0 导致死循环
        if self.speed <= 0.0:
            self.get_logger().error(
                f'speed_mps={self.speed} 非法（必须 > 0），回退为 0.2')
            self.speed = 0.2

        self._action_server = ActionServer(
            self,
            MoveDistance,
            '/move_distance',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
        )
        self.get_logger().info(
            f'Action 服务 /move_distance 已就绪（speed={self.speed} m/s）')

    def goal_callback(self, goal_request):
        """拒绝非正距离的目标。"""
        if goal_request.distance <= 0.0:
            self.get_logger().warning('拒绝目标：distance 必须 > 0')
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """接受取消请求（真正停止在 execute 里处理）。"""
        self.get_logger().info('收到取消请求')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        """执行逻辑：循环累加里程，发反馈，支持取消。"""
        goal = goal_handle.request
        feedback = MoveDistance.Feedback()
        result = MoveDistance.Result()

        traveled = 0.0
        step = self.speed * 0.1     # 每步前进的距离
        step_count = 0              # 用步数计数控制日志频率，避免浮点比较

        self.get_logger().info(f'开始前进 {goal.distance:.2f} m')

        while traveled < goal.distance:
            # 取消处理：必须在循环里检查
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result.success = False
                result.distance_traveled = traveled
                self.get_logger().info(f'已取消，已走 {traveled:.2f} m')
                return result

            # 限制 traveled 不超过目标，避免最后一步"踩过终点"
            traveled = min(traveled + step, goal.distance)
            feedback.progress = min(traveled / goal.distance, 1.0)
            goal_handle.publish_feedback(feedback)

            # 每 10 步（=1 秒）打印一次，语义与注释一致
            step_count += 1
            if step_count % 10 == 0:
                self.get_logger().info(
                    f'进度 {feedback.progress*100:.0f}%，已走 {traveled:.2f} m')

            time.sleep(0.1)

        goal_handle.succeed()
        result.success = True
        result.distance_traveled = traveled
        self.get_logger().info(f'到达目标，共 {traveled:.2f} m')
        return result


def main(args=None):
    rclpy.init(args=args)
    node = MoveActionServer()

    # 关键：多线程执行器，保证 cancel service 不被 execute 阻塞
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
