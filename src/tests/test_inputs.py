from unittest import TestCase
from unittest.mock import patch
import inspect

import ImuNode
import JointStateNode   
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from sensor_msgs.msg import JointState


class TestMyInputClass(TestCase):

    def setUp(self):
        print("Setup")
        if not rclpy.ok():  # Prevent multiple initializations
            rclpy.init()
        self.imu = ImuNode.ImuInput()
        self.joint = JointStateNode.JointStateInput()

    def tearDown(self):
        print("Teardown")
        self.imu.destroy_node()
        self.joint.destroy_node()
        rclpy.shutdown()

    def test_assert_imuSensor_input_msg_type_as_imu(self):
        rclpy.spin_once(self.imu, timeout_sec=1.0) # timeout_sec is important, else it'll wait endlessly
        self.assertIsInstance(self.imu.get_input(), Imu)

    def test_assert_jointState_input_msg_type_as_JointState(self):
        rclpy.spin_once(self.joint, timeout_sec=10.0)
        self.assertIsInstance(self.joint.get_input(), JointState)

    def test_cleaned_imu_is_Yorientation_and_angularVelocity(self):
        rclpy.spin_once(self.imu, timeout_sec=1.0)
        imuValue = self.imu.get_input()

        self.assertIsInstance(imuValue.orientation.y, float)
        self.assertIsInstance(imuValue.angular_velocity.y, float)


