#!/usr/bin/env python3
# Service 客户端：调用 /set_mode，演示异步调用与结果等待
# 教学点：create_client、wait_for_service、call_async、spin_until_future_complete

import sys

import rclpy
from rclpy.node import Node
from rclpy.utilities import remove_ros_args

from my_interfaces.srv import SetMode


class ModeServiceClient(Node):
    """示例客户端：把命令行参数作为目标模式发给服务端。"""

    def __init__(self):
        super().__init__('mode_service_client')
        self.client = self.create_client(SetMode, '/set_mode')

        # 等待服务端上线，避免一上来就 call 失败
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('等待 /set_mode 服务上线...')

        self.request = SetMode.Request()

    def send_request(self, mode: str):
        """异步发送请求并等待结果。"""
        self.request.mode = mode
        # call_async 不阻塞当前线程；再用 spin 等 future
        future = self.client.call_async(self.request)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            response = future.result()
            self.get_logger().info(
                f'响应: success={response.success}, message={response.message}')
            return response
        self.get_logger().error('服务调用失败')
        return None


def main(args=None):
    rclpy.init(args=args)

    # 从命令行读模式，默认 auto
    # remove_ros_args 剔除 --ros-args 部分，避免把 ROS 参数当成业务参数
    argv = remove_ros_args(args=sys.argv)
    mode = 'auto'
    if len(argv) > 1:
        mode = argv[1]

    node = None
    try:
        # 构造函数里会等待服务上线，放进 try 里才能用 Ctrl+C 干净退出
        node = ModeServiceClient()
        node.send_request(mode)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
