import os
import launch
import launch_ros.actions
from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
import launch_testing
import launch_testing.actions

def generate_launch_description():

    bag_path = os.path.join(
        get_package_share_directory('humanoid_robot'),
        'tests', 'sensor_bag'
    )

    # Rosbag2 playback
    bag_play = launch.actions.ExecuteProcess(
        cmd=['ros2', 'bag', 'play', bag_path, '--loop'],
        output='screen'
    )

    imu_node = launch_ros.actions.Node(
        package='humanoid_robot',
        executable='ImuNode.py',
        output='screen'
    )

    joint_node = launch_ros.actions.Node(
        package='humanoid_robot',
        executable='JointStateNode.py',
        output='screen'
    )

    
    return LaunchDescription([
        bag_play,
        imu_node,
        joint_node,
    ])

