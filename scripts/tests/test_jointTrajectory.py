from unittest import TestCase
from unittest.mock import patch

import JointTrajectoryNode
import rclpy



class TestMyJointTrajectoryClass(TestCase):

    def setUp(self):
        print("Setup")
        if not rclpy.ok():  # Prevent multiple initializations
            rclpy.init()
        self.trajectory = JointTrajectoryNode.JointTrajectoryNode()

    def tearDown(self):
        print("Teardown")
        rclpy.shutdown()
        self.trajectory.destroy_node()
    
    def test_joint_trajectory_command_targets_only_one_joint(self):
        joint_value = [0.5]
        joint_name = ["Neck_Yaw"]

        self.trajectory.set_target_trajectory(joint_name, joint_value)

        rclpy.spin_once(self.trajectory, timeout_sec=5.0)

        msg = self.trajectory.get_output()

        joint_names = msg.joint_names
        joint_positions = msg.points[0].positions        

        for i in range(len(joint_names)):
            name = joint_names[i]
            pos = joint_positions[i]
            if name == joint_name[0]:
                self.assertEqual(pos, joint_value[0])
            else:
                self.assertEqual(pos, 0.0)

    def test_joint_trajectory_command_for_multiple_joints(self):
        neck_yaw_value = 0.2
        neck_pitch_value = -0.25
        left_shoulder_pitch_value = -3.0
        right_shoulder_pitch_value = -3.0
        left_shoulder_roll_value = -0.2
        right_shoulder_roll_value = -0.2
        
        joint_name = ["Neck_Yaw", "Neck_Pitch", "TorsoShoulder_Left_Pitch", "TorsoShoulder_Right_Pitch", 
                      "TorsoShoulder_Left_Roll", "TorsoShoulder_Right_Roll"]
        joint_value = [neck_yaw_value, neck_pitch_value, left_shoulder_pitch_value, right_shoulder_pitch_value, 
                       left_shoulder_roll_value, right_shoulder_roll_value]

        self.trajectory.set_target_trajectory(joint_name, joint_value)

        rclpy.spin_once(self.trajectory, timeout_sec=5.0)

        msg = self.trajectory.get_output()

        output_joint_names = msg.joint_names
        output_joint_positions = msg.points[0].positions
        
        for i in range(len(output_joint_names)):
            if output_joint_names[i] in joint_name:
                index = joint_name.index(output_joint_names[i])
                self.assertEqual(output_joint_positions[i], joint_value[index])
            else:
                self.assertEqual(output_joint_positions[i], 0.0)