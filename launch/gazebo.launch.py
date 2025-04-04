from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    pkg_path = get_package_share_directory("humanoid_robot")  # Your package name
    sdf_file = os.path.join(pkg_path, 'urdf', 'robot.sdf')
    world_file = os.path.join(pkg_path, 'worlds', 'custom.world')

    # Launch Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [os.path.join(get_package_share_directory('gazebo_ros'), 'launch'), '/gazebo.launch.py']
        ),
        launch_arguments={'world': world_file}.items()  # 'verbose': 'true',
    )

    # Spawn the robot
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-file', sdf_file, '-entity', 'robot', '-x', '0', '-y', '0', '-z', '0'],
        output='screen'
    )

    # Imu Node
    Imu = Node(
        package='humanoid_robot',
        executable='ImuNode.py',
        output='screen')  
    
    # Joint State Node
    JointState = Node(
        package='humanoid_robot',
        executable='JointStateNode.py',
        output='screen')  

    return LaunchDescription([
        DeclareLaunchArgument(name='headless-rendering', default_value='true', description='Set to "false" to run with GUI.'),
        gazebo,
        spawn_entity,
        Imu,
        JointState,
    ])
