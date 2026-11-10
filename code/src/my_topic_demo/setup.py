from setuptools import find_packages, setup

package_name = 'my_topic_demo'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='laoding',
    maintainer_email='lddzwxy@gmail.com',
    description='S1 模块2：/cmd_vel 发布与订阅',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'velocity_publisher = my_topic_demo.velocity_publisher:main',
            'velocity_subscriber = my_topic_demo.velocity_subscriber:main',
        ],
    },
)
