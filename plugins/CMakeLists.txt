add_library(contact_bridge_plugin SHARED
  contact_bridge_plugin.cpp
)

add_library(reset_joints_plugin SHARED
  reset_joints_plugin.cpp
)

add_library(fixed_base_support_plugin SHARED
  fixed_base_support_plugin.cpp
)

# ROS Plugins
# Include the generated headers from msg
target_include_directories(contact_bridge_plugin PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/../rosidl_generator_cpp>
)

target_include_directories(reset_joints_plugin PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/../rosidl_generator_cpp>
)

# Gazebo Plugins
target_include_directories(fixed_base_support_plugin PRIVATE
  ${gazebo_INCLUDE_DIRS} 
  /usr/include/sdformat-9.7
  /usr/include/ignition/math6
  /usr/include/ignition/common3
  /usr/include/ignition/transport8
  /usr/include/ignition/msgs5
)

# Get the target for the message type support
rosidl_get_typesupport_target(cpp_typesupport_target
  humanoid_robot "rosidl_typesupport_cpp")

# Make sure the plugins depend on the generated message type library
add_dependencies(contact_bridge_plugin ${cpp_typesupport_target})
add_dependencies(reset_joints_plugin ${cpp_typesupport_target})

# Link to the generated message library
target_link_libraries(contact_bridge_plugin ${cpp_typesupport_target})
target_link_libraries(reset_joints_plugin ${cpp_typesupport_target})
target_link_libraries(fixed_base_support_plugin ${gazebo_LIBRARIES}) # Gazebo Plugin

# Find and link external dependencies
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(gazebo_ros REQUIRED)
find_package(gazebo_msgs REQUIRED)

find_package(gazebo REQUIRED) 
find_package(ignition-math6 REQUIRED)
find_package(sdformat9 REQUIRED)

ament_target_dependencies(contact_bridge_plugin
  rclcpp
  std_msgs
  gazebo_ros
  gazebo_msgs
)

ament_target_dependencies(reset_joints_plugin
  rclcpp
  std_msgs
  gazebo_ros
  gazebo_msgs
)

# Install
install(TARGETS contact_bridge_plugin reset_joints_plugin fixed_base_support_plugin
  LIBRARY DESTINATION lib
)
