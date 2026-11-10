from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'my_bringup'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 把 launch / config 装进 share，ros2 launch 才能发现
        (os.path.join('share', package_name, 'launch'),
         glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'),
         glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='laoding',
    maintainer_email='lddzwxy@gmail.com',
    description='S1 模块4：参数与 Launch',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'param_node = my_bringup.param_node:main',
            'sim_sensor = my_bringup.sim_sensor:main',
            'decision_node = my_bringup.decision_node:main',
            'mock_driver = my_bringup.mock_driver:main',
            'lifecycle_demo = my_bringup.lifecycle_demo:main',
        ],
    },
)
