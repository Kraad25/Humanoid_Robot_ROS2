#!/usr/bin/env python3

# Add this, (#!/usr/bin/env python3) at the top to prevent the error, Exec format error.
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from tf_transformations import euler_from_quaternion

from BaseInputClass import BaseInput

class ImuInput(Node, BaseInput):

    def __init__(self):
        super().__init__('imu_reader')
        self.get_logger().info("IMU values are being recorded")

        self.subscribed_to_imuOut  = self.create_subscription(Imu, '/imu_plugin/out', self.imu_callback, 10)
        self.imu_publisher = self.create_publisher(Imu, '/cleaned_imu', 10)
        
        self.cleaned_imu = None
        
        
    def imu_callback(self, msg):
        self.publish_cleaned_input(msg)

    def publish_cleaned_input(self, rawData):
        cleanedImu = self.clean_input(rawData)
        self.imu_publisher.publish(cleanedImu)

    def get_input(self):
        return self.cleaned_imu   
     
    def clean_input(self, raw_imu):
        cleanedImu = Imu()
        quaternion = [raw_imu.orientation.x, raw_imu.orientation.y, raw_imu.orientation.z, raw_imu.orientation.w]
        roll, pitch, yaw = self.get_roll_pitch_yaw(quaternion)

        cleanedImu.orientation.y = pitch
        cleanedImu.angular_velocity.y = raw_imu.angular_velocity.y
                
        self.cleaned_imu = cleanedImu
        return cleanedImu
    
    def get_roll_pitch_yaw(self, quaternion):
        try:
            roll, pitch, yaw = euler_from_quaternion(quaternion)
            return roll, pitch, yaw
        except Exception as e:
            self.get_logger().error(f"Quaternion Conversion Error: {e}")
            raise


if __name__ == '__main__':
    rclpy.init()
    imu_subscriber = ImuInput()
    rclpy.spin(imu_subscriber)
    imu_subscriber.destroy_node()
    rclpy.shutdown()