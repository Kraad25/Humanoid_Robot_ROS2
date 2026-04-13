#!/usr/bin/env python3

# Add this, (#!/usr/bin/env python3) at the top to prevent the error, Exec format error.
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from tf2_ros import Buffer, TransformListener
import tf2_geometry_msgs

import cv2
import numpy as np

class PerceptionNode(Node):
    def __init__(self):
        super().__init__('perception_node')
        self.get_logger().info("Perception Node Started")

        self.bridge = CvBridge()
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

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
        self.pose_publisher = self.create_publisher(
            PoseStamped,
            "/cube_pose",
            10
        )

    # Public Methods
    def left_callback(self, msg):
        self.left_frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        self._process()

    def right_callback(self, msg):
        self.right_frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        self._process()

    # Private Methods  
    def _process(self):
        if self.left_frame is None or self.right_frame is None:
            return

        left_center = self._detect_object(self.left_frame)
        right_center = self._detect_object(self.right_frame)

        if left_center is None or right_center is None:
            return

        xL, yL = left_center
        xR, yR = right_center

        depth = self._compute_depth(xL, xR)

        if depth is None:
            return

        X, Y, Z = self._pixel_to_3d(xL, yL, depth)

        pose = PoseStamped()

        pose.header.frame_id = "eye_left_link"
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = float(X)
        pose.pose.position.y = float(Y)
        pose.pose.position.z = float(Z)

        pose.pose.orientation.w = 1.0

        # Position with respect to the base_link
        try:
            transform = self.tf_buffer.lookup_transform(
                "base_link",              # target frame
                "eye_left_link",          # source frame
                rclpy.time.Time()
            )

            pose_in_base = tf2_geometry_msgs.do_transform_pose(pose.pose, transform)

            pose_out = PoseStamped()
            pose_out.header.frame_id = "base_link"
            pose_out.header.stamp = self.get_clock().now().to_msg()
            pose_out.pose = pose_in_base

            self.pose_publisher.publish(pose_out)

        except Exception as e:
            self.get_logger().warn(f"TF transform failed: {e}")

        self._find_distance(pose_out)

    def _find_distance(self, cube_pose):
        xc = cube_pose.pose.position.x
        yc = cube_pose.pose.position.y
        zc = cube_pose.pose.position.z

        try:
            transform = self.tf_buffer.lookup_transform(
                "base_link",
                "Palm_Left",
                rclpy.time.Time()
            )
        except Exception as e:
            self.get_logger().warn(f"TF failed: {e}")
            return

        xp = transform.transform.translation.x
        yp = transform.transform.translation.y
        zp = transform.transform.translation.z

        dx = xc-xp
        dy = yc-yp
        dz = zc-zp

        distance = np.sqrt(dx*dx+ dy*dy + dz*dz)

        #self.get_logger().info(f"Distance: {distance:.3f} m")
    
    def _detect_object(self, frame):
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
        total_area = M["m00"]

        if total_area == 0:
            return None

        sum_of_x = M["m10"]
        sum_of_y = M["m01"]

        cx = int(sum_of_x / total_area) # Average x of all the pixels
        cy = int(sum_of_y / total_area) # Average y of all the pixels

        return (cx, cy)

    def _compute_depth(self, x_left, x_right):
        disparity = abs(x_left - x_right)

        if disparity == 0:
            return None

        depth = (self.focal_length * self.baseline) / disparity

        return depth

    def _pixel_to_3d(self, x, y, depth):

        # Co-ordinate axes are different, Thus
        X = depth
        Y = - ((x - self.cx) * depth / self.fx)
        Z = - ((y - self.cy) * depth / self.fy)

        return X, Y, Z


if __name__ == "__main__":
    rclpy.init()
    node = PerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()