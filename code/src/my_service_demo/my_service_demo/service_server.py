#!/usr/bin/env python3
# Service 服务端：提供 /set_mode（my_interfaces/srv/SetMode）
# 教学点：create_service、回调填 response、参数校验

import rclpy
from rclpy.node import Node

from my_interfaces.srv import SetMode


class ModeServiceServer(Node):
    """接收模式切换请求，校验后返回 success/message。"""

    # 允许的模式白名单
    ALLOWED_MODES = ('manual', 'auto', 'sport')

    def __init__(self):
        super().__init__('mode_service_server')
        self.current_mode = 'manual'

        # 创建服务：类型、服务名、回调
        self.srv = self.create_service(
            SetMode, '/set_mode', self.set_mode_callback)

        self.get_logger().info('服务 /set_mode 已就绪')

    def set_mode_callback(self, request: SetMode.Request,
                          response: SetMode.Response):
        """请求-响应回调：只做校验与状态更新，不要在里面再同步 call 别的服务。"""
        mode = request.mode
        self.get_logger().info(f'收到设置模式请求: {mode!r}')

        if mode in self.ALLOWED_MODES:
            self.current_mode = mode
            response.success = True
            response.message = f'mode set to {mode}'
            self.get_logger().info(response.message)
        else:
            response.success = False
            response.message = (
                f'invalid mode {mode!r}, allowed: {self.ALLOWED_MODES}')
            self.get_logger().warning(response.message)

        return response


def main(args=None):
    rclpy.init(args=args)
    node = ModeServiceServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
