# 一键启动多节点小系统：感知 → 决策 → 执行
# 用法: ros2 launch my_bringup demo_system.launch.py

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params_file = PathJoinSubstitution([
        FindPackageShare('my_bringup'), 'config', 'params.yaml'])

    return LaunchDescription([
        # 感知层
        Node(
            package='my_bringup',
            executable='sim_sensor',
            name='sim_sensor',
            output='screen',
            parameters=[params_file],
        ),
        # 决策层
        Node(
            package='my_bringup',
            executable='decision_node',
            name='decision_node',
            output='screen',
            parameters=[params_file],
            # 可在此 remap 话题
            # remappings=[('/cmd_vel', '/robot1/cmd_vel')],
        ),
        # 执行层
        Node(
            package='my_bringup',
            executable='mock_driver',
            name='mock_driver',
            output='screen',
        ),
        # 参数心跳演示（可选）
        Node(
            package='my_bringup',
            executable='param_node',
            name='param_node',
            output='screen',
            parameters=[params_file],
        ),
    ])
