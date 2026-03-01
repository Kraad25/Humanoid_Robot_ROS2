#!/usr/bin/env python3

# Add this, (#!/usr/bin/env python3) at the top to prevent the error, Exec format error.
import time
import random

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from data import ALL_JOINTS, DEFAULT_JOINT_POSITION_VALUES

class GestureNode(Node):
    def __init__(self):
        super().__init__("gesture_node")
        self.get_logger().info("GestureNode is running...")

        self.subscription = self.create_subscription(String, "/gesture_command", self.gesture_callback, 10)
        self.publisher = self.create_publisher(JointTrajectory, '/joint_trajectory_controller/joint_trajectory', 10)

        self.GESTURES = {
            "nod": self._perform_nod,
            "head_tilt": self._perform_head_scratch,
            "wave_hand": self._perform_wave_hand,
            "idle_hand_movement": self._perform_idle_movement,
            "lower_head": self._perform_shutdown,
        }

        self._current_state = "idle"
        self.idle_timer = self.create_timer(6.0, self._idle_loop)

    # Public Methods
    def gesture_callback(self, msg):
        gesture_name = msg.data

        if gesture_name in self.GESTURES:
            self.get_logger().info(f"Executing gesture: {gesture_name}")
            self._current_state = "active"
            self.GESTURES[gesture_name]()
            self._current_state = "idle"
        else:
            self.get_logger().warn(f"Unknown gesture: {gesture_name}")

    # Private Methods
    def _send_trajectory(self, keyframes):
        trajectory_msg = JointTrajectory()
        trajectory_msg.joint_names = ALL_JOINTS

        cumulative_time = 0.0

        for joint_dict, duration in keyframes:
            cumulative_time += duration

            point = JointTrajectoryPoint()
            if trajectory_msg.points:
                positions = list(trajectory_msg.points[-1].positions)
            else:
                positions = list(DEFAULT_JOINT_POSITION_VALUES)

            for joint_name, value in joint_dict.items():
                if joint_name in trajectory_msg.joint_names:
                    idx = trajectory_msg.joint_names.index(joint_name)
                    positions[idx] = value

            point.positions = positions
            point.time_from_start.sec = int(cumulative_time)
            point.time_from_start.nanosec = int((cumulative_time % 1) * 1e9)

            trajectory_msg.points.append(point)

        self.publisher.publish(trajectory_msg)

    def _idle_loop(self):
        if self._current_state == "idle":
            self._idle_breath()
    
    def _perform_nod(self):        
        self._send_trajectory([
            # Tilt Down step by step
            ({"Neck_Pitch": 0.0}, 0.5),
            ({"Neck_Pitch": 0.05}, 0.5),
            ({"Neck_Pitch": 0.1}, 0.5),
            ({"Neck_Pitch": 0.15}, 0.5),
            ({"Neck_Pitch": 0.20}, 0.5),

            # Recover step by step
            ({"Neck_Pitch": 0.15}, 0.5),
            ({"Neck_Pitch": 0.1}, 0.5),
            ({"Neck_Pitch": 0.05}, 0.5),
            ({"Neck_Pitch": 0.0}, 0.5),
        ])

    def _perform_idle_movement(self):
        idle_variants = [
            self._idle_head_micro_adjustments,
        ]
        random.choice(idle_variants)()

    def _perform_head_scratch(self):
        self._send_trajectory([
            # Start
            ({"Neck_Yaw": -0.0, "Neck_Pitch": -0.0}, 1.0),            
            
            # Slight head tilt with arm lifting toward temple step-1
            ({
                "Neck_Yaw": -0.6, 
                "Neck_Pitch": -0.08,
                "TorsoShoulder_Right_Pitch": -1.0,
                "TorsoShoulder_Right_Roll": 0.1, 
                "ShoulderElbow_Right": -0.392699
            }, 1.0),

            # Slight head tilt with arm lifting toward temple step-2
            ({
                "Neck_Yaw": -0.8, 
                "Neck_Pitch": -0.1,
                "TorsoShoulder_Right_Pitch": -2.5,
                "TorsoShoulder_Right_Roll": 0.45, 
                "ShoulderElbow_Right": -1.0
            }, 1.0),

            # Head Scratch
            ({"ShoulderElbow_Right": -1.74533}, 1.0),
            ({"ShoulderElbow_Right": -1.0}, 1.0),
            ({"ShoulderElbow_Right": -1.74533}, 1.0),

            # Recovery step-1
            ({"Neck_Yaw": -0.6, "Neck_Pitch": -0.08}, 1.0),

            # Recovery step-2
            ({
                "Neck_Yaw": 0.0, 
                "Neck_Pitch": 0.0,
                "TorsoShoulder_Right_Pitch": 0.0,
                "TorsoShoulder_Right_Roll": 0.0, 
                "ShoulderElbow_Right": 0.0
            }, 1.0),
        ])
        
    def _perform_wave_hand(self):
        self._send_trajectory([
            # Raise Arm
            ({"ShoulderElbow_Left": -0.392699, "TorsoShoulder_Left_Roll": -0.1}, 0.5),
            ({
                "ShoulderElbow_Left": -0.785398, 
                "TorsoShoulder_Left_Roll": -0.2, 
                "TorsoShoulder_Right_Pitch": -1.57, 
                "ShoulderElbow_Right": 0.0
            }, 0.5),
            ({"TorsoShoulder_Right_Pitch": -3.14159}, 0.5),                    

            # Wave oscillations
            ({"TorsoShoulder_Right_Roll": 0.4}, 0.5),
            ({"TorsoShoulder_Right_Roll": 0.3, "TorsoShoulder_Left_Roll": -0.15}, 0.5),
            ({"TorsoShoulder_Right_Roll": 0.2}, 0.5),
            ({"TorsoShoulder_Right_Roll": 0.1, "TorsoShoulder_Left_Roll": -0.1}, 0.5),
            ({"TorsoShoulder_Right_Roll": 0.0}, 0.5),
            ({"TorsoShoulder_Right_Roll": 0.1, "TorsoShoulder_Left_Roll": -0.15}, 0.5),
            ({"TorsoShoulder_Right_Roll": 0.2}, 0.5),

            # Return
            ({
                "TorsoShoulder_Right_Pitch": 0.0,
                "ShoulderElbow_Right": 0.0,
                "ShoulderElbow_Left": 0.0,
                "TorsoShoulder_Right_Roll": 0.0,
                "TorsoShoulder_Left_Roll": 0.0,            
            }, 0.5),
        ])

    def _perform_shutdown(self):
        self._send_trajectory([
            # Neck Down / Shutdown
            ({"Neck_Pitch": 0.3}, 1.2),
        ])

    def _idle_breath(self):
        self._send_trajectory([

            # Inhale
            ({"TorsoShoulder_Left_Roll": -0.04,
            "TorsoShoulder_Right_Roll": 0.04}, 3.0),

            # Exhale
            ({"TorsoShoulder_Left_Roll": 0.0,
            "TorsoShoulder_Right_Roll": 0.0}, 3.0),
        ])
    
    def _idle_head_micro_adjustments(self):
        drift = random.uniform(-0.3, 0.3)

        self._send_trajectory([

            # Random micro adjustments
            ({"Neck_Yaw": drift}, 2.0),
            ({"Neck_Yaw": drift * 0.3}, 1.5),
            ({"Neck_Yaw": 0.0}, 2.0),
        ])

if __name__ == '__main__':
    rclpy.init()
    gesture = GestureNode()
    rclpy.spin(gesture)
    gesture.destroy_node()
    rclpy.shutdown()