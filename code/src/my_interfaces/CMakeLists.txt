# my_interfaces：自定义接口包（ament_cmake + rosidl）
cmake_minimum_required(VERSION 3.8)
project(my_interfaces)

# C++17 为 Jazzy 常用基线
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)

# 生成自定义接口：列出所有 .msg / .srv / .action
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/RobotStatus.msg"
  "srv/SetMode.srv"
  "action/MoveDistance.action"
  DEPENDENCIES std_msgs builtin_interfaces geometry_msgs
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
