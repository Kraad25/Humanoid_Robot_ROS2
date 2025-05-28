from unittest import TestCase
from unittest.mock import patch
import inspect

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from sensor_msgs.msg import JointState

from Controller import Logic

class TestMyInputClass(TestCase):

    def setUp(self):
        print("Setup")
        if not rclpy.ok():  # Prevent multiple initializations
            rclpy.init()

    def tearDown(self):
        print("Teardown")
        rclpy.shutdown()

    def test_extending_the_arms(self):
        logic = Logic()

        logic.extending_arms()
        arm_positions = logic.jointState
        self.assertTrue(abs(arm_positions['RightShoulder']) - 1.57 < 0.05 )
        self.assertTrue(abs(arm_positions['RightElbow']) - 1.57 < 0.05 )