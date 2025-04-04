#!/usr/bin/env python3

# Add this, (#!/usr/bin/env python3) at the top to prevent the error, Exec format error.
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from sensor_msgs.msg import JointState
from tf_transformations import euler_from_quaternion

from abc import ABC, abstractmethod

class BaseInput(ABC):
    
    @abstractmethod
    def get_input(self):
        pass

    @abstractmethod
    def clean_input(self):
        pass

    @abstractmethod
    def publish_cleaned_input(self, msg):
        pass