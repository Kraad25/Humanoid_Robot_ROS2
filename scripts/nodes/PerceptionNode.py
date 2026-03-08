#!/usr/bin/env python3

# Add this, (#!/usr/bin/env python3) at the top to prevent the error, Exec format error.
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2
import numpy as np

class PerceptionNode(Node):
    def __init__(self):
        super().__init__('perception_node')
        self.get_logger().info("Perception Node Started")

        self.bridge = CvBridge()

        self.left_frame = None
        self.right_frame = None

        # camera parameters
        self.baseline = 0.036
        self.focal_length = 277.191356

        self.fx = 277.191356
        self.fy = 277.191356
        self.cx = 160.5
        self.cy = 120.5

        self.left_eye_subscription = self.create_subscription(
            Image,
            '/eye_left/image_raw',
            self.left_callback,
            10
        )
        self.right_eye_subscription = self.create_subscription(
            Image,
            '/eye_right/image_raw',
            self.right_callback,
            10
        )

    def left_callback(self, msg):
        self.left_frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        self.process()

    def right_callback(self, msg):
        self.right_frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        self.process()

    def detect_object(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_red1 = np.array([0,120,70])
        upper_red1 = np.array([10,255,255])

        lower_red2 = np.array([170,120,70])
        upper_red2 = np.array([180,255,255])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

        mask = mask1 + mask2

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            return None

        largest = max(contours, key=cv2.contourArea)

        M = cv2.moments(largest)

        if M["m00"] == 0:
            return None

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        return (cx, cy)

    def compute_depth(self, x_left, x_right):
        disparity = abs(x_left - x_right)

        if disparity == 0:
            return None

        depth = (self.focal_length * self.baseline) / disparity

        return depth

    def process(self):
        if self.left_frame is None or self.right_frame is None:
            return

        left_center = self.detect_object(self.left_frame)
        right_center = self.detect_object(self.right_frame)

        if left_center is None or right_center is None:
            return

        xL, yL = left_center
        xR, yR = right_center

        depth = self.compute_depth(xL, xR)

        if depth is None:
            return

        X, Y, Z = self.pixel_to_3d(xL, yL, depth)

        self.get_logger().info(
            f"Cube position (camera frame): X={X:.2f} Y={Y:.2f} Z={Z:.2f}"
        )

        cv2.circle(self.left_frame, (xL, yL), 1, (0,255,0), -1)
        cv2.circle(self.right_frame, (xR, yR), 1, (0,255,0), -1)

        cv2.imshow("Left", self.left_frame)
        cv2.imshow("Right", self.right_frame)

        cv2.waitKey(1)

    def pixel_to_3d(self, x, y, depth):

        X = (x - self.cx) * depth / self.fx
        Y = (y - self.cy) * depth / self.fy
        Z = depth

        return X, Y, Z


if __name__ == "__main__":
    rclpy.init()
    node = PerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()