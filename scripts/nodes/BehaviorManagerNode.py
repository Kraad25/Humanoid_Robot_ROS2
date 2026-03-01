#!/usr/bin/env python3

# Add this, (#!/usr/bin/env python3) at the top to prevent the error, Exec format error.
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class BehaviorManagerNode(Node):
    def __init__(self):
        super().__init__("behavior_manager")
        self.get_logger().info("Behavior Manager is running")

        self.llm_sub = self.create_subscription(
            String, "/llm_output", self.llm_callback, 10
        )
        self.gesture_pub = self.create_publisher(String, "/gesture_command", 10)


    def llm_callback(self, msg):
        data = json.loads(msg.data)

        gestures = data.get("gesture", [])

        for gesture in gestures:
            gesture_msg = String()
            gesture_msg.data = gesture
            self.gesture_pub.publish(gesture_msg)

if __name__ == "__main__":
    rclpy.init()
    node = BehaviorManagerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()