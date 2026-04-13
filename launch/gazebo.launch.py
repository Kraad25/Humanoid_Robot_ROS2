from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import TimerAction
import os
import xacro
import yaml
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    pkg_path = get_package_share_directory("humanoid_robot")  # Your package name
    urdf_file = os.path.join(pkg_path, 'urdf', 'robot.urdf.xacro')
    world_file = os.path.join(pkg_path, 'worlds', 'custom.world')

    robot_description_xml = xacro.process_file(urdf_file).toxml()

    robot_description = ParameterValue(
        robot_description_xml,
        value_type=str
    )

    robot_state_publisher = Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    output='screen',
    parameters=[{'robot_description': robot_description}]
    )

    # Launch Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [os.path.join(get_package_share_directory('gazebo_ros'), 'launch'), '/gazebo.launch.py']),
            launch_arguments={'headless': LaunchConfiguration('headless-rendering'),
                              'world': world_file, 'gui': 'true'}.items()  # , 'verbose': 'true'
    )


    # Spawn the robot
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', '/robot_description', 
            '-entity', 'Selene', 
            '-x', '0', '-y', '0', '-z', '0',   # Adjust the z value
            '-timeout', '60'
        ],
        output='screen'
    )
    
    load_joint_controller = TimerAction(
    period=3.0,  # seconds
    actions=[
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['joint_trajectory_controller'],
            output='screen'
            )
        ]
    )

    # Imu Node
    Imu = Node(
        package='humanoid_robot',
        executable='ImuNode.py',
        output='screen'
    )  
    
    # Joint State Node
    JointState = Node(
        package='humanoid_robot',
        executable='JointStateNode.py',
        output='screen'
    )
    
    # Perception Node
    Perception = Node(
        package='humanoid_robot',
        executable='PerceptionNode.py',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    # Gesture Node
    Gesture = Node(
        package='humanoid_robot',
        executable='GestureNode.py',
        output='screen'
    )

    # LLM Node
    LLM = Node(
        package='humanoid_robot',
        executable='LLMNode.py',
        output='screen'
    )

    # Behavior Manager Node
    BehaviorManager = Node(
        package='humanoid_robot',
        executable='BehaviorManagerNode.py',
        output='screen'
    )

    # Pick and Place Node
    PickandPlace = Node(
        package='humanoid_robot',
        executable='PickandPlaceNode.py',
        output='screen'
    )
    
    return LaunchDescription([
        DeclareLaunchArgument(name='headless-rendering', default_value='true', description='Set to "false" to run with GUI.'),
        gazebo,
        robot_state_publisher,
        spawn_entity,
        load_joint_controller,
        Imu,
        JointState,
        Perception,
        PickandPlace,
        #Gesture,
        #BehaviorManager,
        #LLM,
    ])
