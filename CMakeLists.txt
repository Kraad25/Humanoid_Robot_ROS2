cmake_minimum_required(VERSION 3.8)
project(humanoid_robot)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)

find_package(geometry_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(std_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)


rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Contact.msg"
  "msg/Contacts.msg"
  DEPENDENCIES geometry_msgs std_msgs builtin_interfaces
)
add_subdirectory(plugins)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()


install(DIRECTORY meshes urdf worlds launch config
DESTINATION share/${PROJECT_NAME})

install(DIRECTORY scripts/nodes/tests/sensor_bag
DESTINATION share/${PROJECT_NAME}/tests )

install(PROGRAMS scripts/nodes/ImuNode.py scripts/nodes/JointStateNode.py
DESTINATION lib/${PROJECT_NAME})

ament_package()
