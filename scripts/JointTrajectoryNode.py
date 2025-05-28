#!/usr/bin/env python3

# Add this, (#!/usr/bin/env python3) at the top to prevent the error, Exec format error.
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class JointTrajectoryNode(Node):
    def __init__(self):
        super().__init__('joint_trajectory_node')
        self.get_logger().info("Joint Trajectory Node initialized")
        
        self.publisher = self.create_publisher(JointTrajectory, '/joint_trajectory_controller/joint_trajectory', 10)
        self.subscription = self.create_subscription(JointTrajectory, '/joint_trajectory_controller/joint_trajectory', self.trajectory_callback, 10)

        self.ALL_JOINTS = ["Neck_Yaw", "Neck_Pitch", "TorsoShoulder_Left_Pitch", "TorsoShoulder_Left_Roll",
                                          "ShoulderElbow_Left", "TorsoShoulder_Right_Pitch", "TorsoShoulder_Right_Roll",
                                          "ShoulderElbow_Right", "TorsoThigh_Left_Pitch", "TorsoThigh_Left_Yaw",
                                          "ThighCalf_Left", "CalfFoot_Left", "TorsoThigh_Right_Pitch",
                                          "TorsoThigh_Right_Yaw", "ThighCalf_Right", "CalfFoot_Right"
                        ]
        self.DEFAULT_JOINT_POSITION_VALUES = [0.0] * len(self.ALL_JOINTS)

    def publish_trajectory(self, trajectory_msg):
        self.publisher.publish(trajectory_msg)

    def set_target_trajectory(self, joint_name, value, time_to_end_sec=1):
        trajectory_msg = JointTrajectory()
        trajectory_msg.joint_names = self.ALL_JOINTS
        
        trajectory_msg.points.append(JointTrajectoryPoint())
        trajectory_msg.points[0].positions = self.DEFAULT_JOINT_POSITION_VALUES

        for i in range(len(joint_name)):
            if joint_name[i] in trajectory_msg.joint_names:
                index = trajectory_msg.joint_names.index(joint_name[i])
                trajectory_msg.points[0].positions[index] = value[i]
                
        trajectory_msg.points[0].time_from_start.sec = time_to_end_sec  # Set time from start to 1 second

        self.publish_trajectory(trajectory_msg)

    def trajectory_callback(self, msg):
        self.get_logger().info(f"Received trajectory: {msg.joint_names}")
        self.last_msg = msg

    def get_output(self):
        return self.last_msg