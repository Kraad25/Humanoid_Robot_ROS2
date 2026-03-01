#!/usr/bin/env python3

# Add this, (#!/usr/bin/env python3) at the top to prevent the error, Exec format error.
import json
import threading
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ConversationNode(Node):
    def __init__(self):
        super().__init__("conversation_node")
        self.get_logger().info("Ready to converse")

        self.publisher = self.create_publisher(String, "/user_input", 10)
        self.llm_sub = self.create_subscription(
            String, "/llm_output", self.llm_callback, 10
        )

        self.waiting_for_reply = False
        
        threading.Thread(target=self._conversation_loop, daemon=True).start()

    def _conversation_loop(self):
        while rclpy.ok():
            if not self.waiting_for_reply:
                user_text = input("You: ")

                if user_text.lower() in {"exit", "quit"}:
                    rclpy.shutdown()
                    break

                msg = String()
                msg.data = user_text
                self.publisher.publish(msg)

                self.waiting_for_reply = True

    def llm_callback(self, msg):
        data = json.loads(msg.data)

        speech = data.get("speech", "")
        print(f"Selene: {speech}")

        self.waiting_for_reply = False


if __name__ == "__main__":
    rclpy.init()
    node = ConversationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()