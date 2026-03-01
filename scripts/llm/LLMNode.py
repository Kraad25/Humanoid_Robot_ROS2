#!/usr/bin/env python3

# Add this, (#!/usr/bin/env python3) at the top to prevent the error, Exec format error.
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from selene import Selene

class LLMNode(Node):
    def __init__(self):
        super().__init__("llm_node")
        self.get_logger().info("LLM is running")
        self.selene = Selene()

        self.subscription = self.create_subscription(
            String, "/user_input", self.user_callback, 10
        )

        self.publisher = self.create_publisher(String, "/llm_output", 10)

    def user_callback(self, msg):
        user_text = msg.data

        reply = self.selene.handle_input(user_text)

        ros_msg = String()
        ros_msg.data = json.dumps(reply)

        self.publisher.publish(ros_msg)


if __name__ == "__main__":
    rclpy.init()
    node = LLMNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()