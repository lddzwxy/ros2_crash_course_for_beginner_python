#!/usr/bin/env python3
# 练习：打印当前时间（模块0 小作业）
# 运行: python3 print_time.py

from datetime import datetime


def main():
    now = datetime.now()
    print('当前时间:', now.strftime('%Y-%m-%d %H:%M:%S'))
    print('这是 ROS2 课程的第一个 Python 脚本，干得漂亮！')


if __name__ == '__main__':
    main()
