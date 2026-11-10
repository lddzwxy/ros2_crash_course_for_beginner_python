#!/usr/bin/env python3
# 练习：MiniRobot 类（模块0.6）
# 覆盖：类、属性、方法、异常处理
# 运行: python3 mini_robot.py


class MiniRobot:
    """一个极简机器人：能开、能停、有电量。"""

    def __init__(self, name: str, battery: float = 100.0):
        self.name = name
        self.battery = battery
        self.speed = 0.0
        print(f'[{self.name}] 启动成功，电量 {self.battery}%')

    def set_speed(self, speed: float):
        """设置速度，范围 -1.0 ~ 1.0。"""
        if self.battery <= 0:
            raise RuntimeError('电量耗尽，无法加速')
        if speed < -1.0 or speed > 1.0:
            raise ValueError(f'速度必须在 [-1, 1]，收到 {speed}')
        self.speed = speed
        self.battery -= abs(speed) * 5
        print(f'[{self.name}] 速度={self.speed:.2f}, 电量={self.battery:.1f}%')

    def stop(self):
        self.speed = 0.0
        print(f'[{self.name}] 已停车')


def main():
    bot = MiniRobot('小蓝')
    try:
        bot.set_speed(0.5)
        bot.set_speed(1.5)  # 应触发 ValueError
    except ValueError as e:
        print('捕获到异常:', e)
    finally:
        bot.stop()


if __name__ == '__main__':
    main()
