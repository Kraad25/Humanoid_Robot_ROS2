add_library(contact_bridge_plugin SHARED
  contact_bridge_plugin.cpp
)

# Include the generated headers from msg
target_include_directories(contact_bridge_plugin PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/../rosidl_generator_cpp>
)

# Get the target for the message type support
rosidl_get_typesupport_target(cpp_typesupport_target
  humanoid_robot "rosidl_typesupport_cpp")

# Make sure the plugin depends on the generated message type library
add_dependencies(contact_bridge_plugin ${cpp_typesupport_target})

# Link to the generated message library
target_link_libraries(contact_bridge_plugin ${cpp_typesupport_target})

# Find and link external dependencies
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(gazebo_ros REQUIRED)
find_package(gazebo_msgs REQUIRED)

ament_target_dependencies(contact_bridge_plugin
  rclcpp
  std_msgs
  gazebo_ros
  gazebo_msgs
)

# Install
install(TARGETS contact_bridge_plugin
  LIBRARY DESTINATION lib
)
