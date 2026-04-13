#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from gazebo_msgs.srv import SetEntityState

from std_msgs.msg import String
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.action import FollowJointTrajectory

from tf2_ros import Buffer, TransformListener
import tf_transformations as tft

from data import ALL_JOINTS, DEFAULT_JOINT_POSITION_VALUES


class MotionNode(Node):
    def __init__(self):
        super().__init__("motion_node")
        self.get_logger().info("MotionNode is running...")

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.set_state_client = self.create_client(SetEntityState, '/set_entity_state')

        self.subscription = self.create_subscription(String, "/motion_command", self.command_callback, 10)

        self._action_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/joint_trajectory_controller/follow_joint_trajectory'
        )

        self.get_logger().info("Waiting for trajectory server...")
        self._action_client.wait_for_server()
        self.get_logger().info("Trajectory server ready.")

        self.COMMANDS = {
            "home": self._home,
            "look_down": self._look_down,
            "look_down_pick": self._look_down_pick,
            "extend_forward": self._extend_forward,
            "elbow_extend": self._extend_forward_elbowbent,
            "grab": self._grab,
            "release": self.release,
        }

        self.grasped = False
        self.timer = self.create_timer(0.005, self._update_grab)

    def command_callback(self, msg):
        cmd = msg.data.strip()

        if cmd in self.COMMANDS:
            self.get_logger().info(f"Executing: {cmd}")
            self.COMMANDS[cmd]()
        else:
            self.get_logger().warn(f"Unknown command: {cmd}")

    def _send_trajectory(self, keyframes):
        traj = JointTrajectory()
        traj.joint_names = ALL_JOINTS

        cumulative_time = 0.0

        for joint_dict, duration in keyframes:
            cumulative_time += duration

            point = JointTrajectoryPoint()

            if traj.points:
                positions = list(traj.points[-1].positions)
            else:
                positions = list(DEFAULT_JOINT_POSITION_VALUES)

            for joint, value in joint_dict.items():
                if joint in traj.joint_names:
                    idx = traj.joint_names.index(joint)
                    positions[idx] = value

            point.positions = positions
            point.time_from_start.sec = int(cumulative_time)
            point.time_from_start.nanosec = int((cumulative_time % 1) * 1e9)

            traj.points.append(point)

        goal = FollowJointTrajectory.Goal()
        goal.trajectory = traj

        self._action_client.send_goal_async(goal)

    def _home(self):
        self._send_trajectory([
            ({}, 2.0)  # default position
        ])

    def _look_down(self):
        self._send_trajectory([
            ({"Neck_Pitch": 0.0}, 0.5),
            ({"Neck_Pitch": 0.05}, 0.5),
            ({"Neck_Pitch": 0.1}, 0.5),
            ({"Neck_Pitch": 0.15}, 0.5),
            ({"Neck_Pitch": 0.20}, 0.5),
            ({"Neck_Pitch": 0.25}, 0.5),
            ({"Neck_Pitch": 0.3}, 0.5),
            ({"Neck_Pitch": 0.35}, 0.5),
            ({"Neck_Pitch": 0.4}, 0.5),
            ({"Neck_Pitch": 0.45}, 0.5),
            ({"Neck_Pitch": 0.5}, 0.5),
            ({"Neck_Yaw": -0.6}, 0.5),
            
        ])

    
    def _look_down_pick(self):
        self._send_trajectory([
            ({"Neck_Pitch": 0.20}, 0.5),
            ({"Neck_Pitch": 0.25}, 0.5),
            ({"Neck_Pitch": 0.3}, 0.5),
            ({"Neck_Pitch": 0.5}, 0.5),
            ({"Neck_Yaw": -0.6}, 0.5),

            ({"ShoulderElbow_Left": -0.4363325,}, 0.5),
            ({"ShoulderElbow_Left": -0.872665,}, 0.5),
            ({"ShoulderElbow_Left": -1.35,}, 0.5),
            ({"ShoulderElbow_Left": -1.7,}, 0.5),

            ({"TorsoShoulder_Left_Pitch": -0.5,}, 0.5),            

            ({"ShoulderElbow_Left": -1.3,}, 0.5),

        ])

    def _extend_forward(self):
        self._send_trajectory([
            ({"TorsoShoulder_Left_Pitch": 0.349066,}, 0.5),
            ({"TorsoShoulder_Left_Pitch": 0.0,}, 0.5),
            ({"TorsoShoulder_Left_Pitch": -1.04719,}, 0.5),
            ({"TorsoShoulder_Left_Pitch": -2.09438,}, 0.5),
            ({"TorsoShoulder_Left_Pitch": -3.00,}, 0.5),
        ])

    def _extend_forward_elbowbent(self):
        self._send_trajectory([
            ({"ShoulderElbow_Left": 0.349066,}, 0.5),
            ({"ShoulderElbow_Left": 0.349066,}, 0.5),
            ({"ShoulderElbow_Left": -0.4363325,}, 0.5),
            ({"ShoulderElbow_Left": -0.872665,}, 0.5),
            ({"ShoulderElbow_Left": -1.35,}, 0.5),
            ({"ShoulderElbow_Left": -1.7,}, 0.5),

            ({"TorsoShoulder_Left_Pitch": -1.04719,}, 0.5),
            ({"TorsoShoulder_Left_Pitch": -2.09438,}, 0.5),
            ({"TorsoShoulder_Left_Pitch": -3.00,}, 0.5),
        ])

    def _grab(self):
        self.grasped = True
        
        req = SetEntityState.Request()
        req.state.name = "red_cube"

        req.state.reference_frame = "base_link"

        req.state.twist.linear.x = 0.0
        req.state.twist.linear.y = 0.0
        req.state.twist.linear.z = 0.0

        req.state.twist.angular.x = 0.0
        req.state.twist.angular.y = 0.0
        req.state.twist.angular.z = 0.0

        self.set_state_client.call_async(req)

    def _update_grab(self):
        if not self.grasped:
            return
        
        try:
            palm = self.tf_buffer.lookup_transform(
                "base_link",
                "Palm_Left",
                rclpy.time.Time()   
            )
        except Exception as e:
            self.get_logger().warn(f"TF failed: {e}")
            return
        
        xp = palm.transform.translation.x
        yp = palm.transform.translation.y
        zp = palm.transform.translation.z

        qx = palm.transform.rotation.x
        qy = palm.transform.rotation.y
        qz = palm.transform.rotation.z
        qw = palm.transform.rotation.w

        palm_q = [qx, qy, qz, qw]
        corr_q = tft.quaternion_from_euler(0, 1.57, 0)

        final_q = tft.quaternion_multiply(palm_q, corr_q)

        req = SetEntityState.Request()
        req.state.name = "red_cube"

        offset = 0.015
        req.state.pose.position.x = xp + offset
        req.state.pose.position.y = yp
        req.state.pose.position.z = zp - 0.01

        req.state.twist.linear.x = 0.0
        req.state.twist.linear.y = 0.0
        req.state.twist.linear.z = 0.0

        req.state.twist.angular.x = 0.0
        req.state.twist.angular.y = 0.0
        req.state.twist.angular.z = 0.0

        req.state.pose.orientation.x = final_q[0]
        req.state.pose.orientation.y = final_q[1]
        req.state.pose.orientation.z = final_q[2]
        req.state.pose.orientation.w = final_q[3]

        self.set_state_client.call_async(req)        

    def release(self):
        self.grasped = False

if __name__ == "__main__":
    rclpy.init()
    node = MotionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

    # Work Envelope

    ## Front Sweep
    ### Joints are straight
        # Max X, Z = (0.254, 0.757) (Forward)
        # Max X, Z = (-0.018, 1.07) (At the top)
        # Min X, Z = (-0.004, 0.495) (At the bottom)

    ### Elbows bent
        # Max X, Z = (0.134, 0.780) (Forward)
        # Max X, Z = (-0.148, 1.07) (At the top, Elbows going behind the back)
        # Min X, Z = (-0.049, 0.493) (At the bottom, Elbows bent)

    ## Side Sweep
    ### Joints are straight
        # Max Y, Z = (-0.332, 0.670) (At the Max Extension, Note that the joint limit is from 0-60... So max is 60)
        # Min Y, Z = (-0.108, 0.495) (At the bottom)

    ### Elbows bent
        # Max Y, Z = (-0.172, 0.757) (At the Max Extension, Note that the joint limit is from 0-60... So max is 60)
        # Min Y, Z = (-0.108, 0.495) (At the bottom)