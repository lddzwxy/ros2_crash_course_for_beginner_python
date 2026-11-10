from setuptools import find_packages, setup

package_name = 'my_action_demo'

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
    description='S1 模块3：Action 示例',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'move_server = my_action_demo.move_server:main',
            'move_client = my_action_demo.move_client:main',
        ],
    },
)
