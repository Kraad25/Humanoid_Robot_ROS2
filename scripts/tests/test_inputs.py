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

    def test_if_ImuNode_cleaned_the_input(self):
        rclpy.spin_once(self.imu, timeout_sec=1.0) # timeout_sec is important, else it'll wait endlessly

        msg = self.imu.get_input()
        self.assertIsInstance(msg , Imu)

        allowed_fields = {("orientation", "y"), ("angular_velocity", "y")}
        for field in ["orientation", "angular_velocity", "linear_acceleration"]:
            for axis in ["x", "y", "z"]:
                value = getattr(getattr(msg, field), axis)
                if (field, axis) in allowed_fields:
                    self.assertNotEqual(value, 0.0)
                else:
                    self.assertEqual(value, 0.0)


    def test_if_JointStateNode_cleaned_the_input(self):
        rclpy.spin_once(self.joint, timeout_sec=10.0)
        msg = self.joint.get_input()

        self.assertIsInstance(msg , JointState)
        self.assertTrue(msg.name)
        self.assertTrue(msg.position)
        self.assertFalse(msg.velocity)
        self.assertFalse(msg.effort)



