#!/usr/bin/env python3

# Add this, (#!/usr/bin/env python3) at the top to prevent the error, Exec format error.
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from sensor_msgs.msg import JointState
from tf_transformations import euler_from_quaternion

from abc import ABC, abstractmethod
from BaseInputClass import BaseInput

class JointStateInput(Node, BaseInput):
    
    def __init__(self):
        super().__init__('Joint_State')
        self.get_logger().info("Joint State is being recorded")
        self.subscribed_to_jointState = self.create_subscription(JointState, '/joint_states', self.joint_state_callback, 10)
        self.jointState_publisher = self.create_publisher(JointState, '/cleaned_jointState', 10)

        self.cleaned_jointState = None

    def joint_state_callback(self, msg):
        self.publish_cleaned_input(msg)

    
    def publish_cleaned_input(self, rawData):
        cleanedJointState = self.clean_input(rawData)
        self.jointState_publisher.publish(cleanedJointState)

    def get_input(self):
        return self.cleaned_jointState.name, self.cleaned_jointState.position
    
    def clean_input(self, rawData):
        cleanedJointState = JointState()

        cleanedJointState.name = rawData.name
        cleanedJointState.position = rawData.position

        self.cleaned_jointState = cleanedJointState

        return cleanedJointState
        
    
if __name__ == '__main__':
    rclpy.init()
    jointState_subscriber = JointStateInput()
    rclpy.spin(jointState_subscriber)
    jointState_subscriber.destroy_node()
    rclpy.shutdown()