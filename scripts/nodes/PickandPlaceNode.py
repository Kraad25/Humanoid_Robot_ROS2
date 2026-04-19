#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

import math
import tf_transformations as tft
from tf2_ros import Buffer, TransformListener

from std_msgs.msg import String
from std_msgs.msg import Float32
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.action import FollowJointTrajectory
from geometry_msgs.msg import PoseStamped

from gazebo_msgs.srv import SetEntityState

from data import ALL_JOINTS, DEFAULT_JOINT_POSITION_VALUES

class MotionNode(Node):
    def __init__(self):
        super().__init__("motion_node")
        self.get_logger().info("MotionNode is running...")

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.set_state_client = self.create_client(SetEntityState, '/set_entity_state')
        self._action_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/joint_trajectory_controller/follow_joint_trajectory'
        )

        self.get_logger().info("Waiting for trajectory server...")
        self._action_client.wait_for_server()
        self.get_logger().info("Trajectory server ready.")

        # Subscriptions
        self.input_subscription = self.create_subscription(String, "/motion_command", self.command_callback, 10)
        self.cube_pose = self.create_subscription(PoseStamped, "/cube_pose",self.cubePose_callback, 10)

        # Publisher
        self.distance_pub = self.create_publisher(Float32, "/distance", 10)

        # Timers
        self.startup_timer = self.create_timer(2.0, self._startup_motion)
        self.timer = self.create_timer(0.005, self._update_grab)

        self.COMMANDS = {
            "home": self._home,
            "look_down": self._look_down,
            "extend_forward": self._extend_forward,
            "grab": self._grab,
            "release": self.release,
        }

        # Grabbing
        self.current_positions = list(DEFAULT_JOINT_POSITION_VALUES)
        self._grasped = False
        self._distance = None
        self.pick_timer = None

    def command_callback(self, msg):
        cmd = msg.data.strip()

        if cmd in self.COMMANDS:
            self.get_logger().info(f"Executing: {cmd}")
            self.COMMANDS[cmd]()
        else:
            self.get_logger().warn(f"Unknown command: {cmd}")

    def cubePose_callback(self, msg):
        self._find_distance(msg)

    def _startup_motion(self):
        self.get_logger().info("Starting initial motion...")
        self._look_down()
        self.startup_timer.cancel()

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

        distance = math.sqrt(dx*dx+ dy*dy + dz*dz)
        self._distance = distance
        self.distance_pub.publish(Float32(data=distance))


    # Trajectory commands
    def _home(self):
        joint_dict = {}

        for i, joint in enumerate(ALL_JOINTS):
            joint_dict[joint] = DEFAULT_JOINT_POSITION_VALUES[i]

        self._send_trajectory([
            (joint_dict, 2.0)
        ])

    def _move_to_target(self, target_dict, duration=2.0, steps=10):
        current = list(self.current_positions)
        target = list(current)

        for joint, value in target_dict.items():
            if joint in ALL_JOINTS:
                index = ALL_JOINTS.index(joint)
                target[index] = value

        traj = JointTrajectory()
        traj.joint_names = ALL_JOINTS

        intermediate_points = []

        for i in range(1, steps+1):
            time = i/steps

            s = 3*(time**2) - 2*(time**3) # A cubic function which goes from 0 to 1 smoothly. 3t^2 - 2t^3.

            positions = []

            for j in range(len(current)):
                pos = current[j] + s * (target[j] - current[j])
                positions.append(pos)
            
            time_from_start = duration * time            
            point = JointTrajectoryPoint()
            
            point.positions = positions            
            point.time_from_start.sec = int(time_from_start)
            point.time_from_start.nanosec = int((time_from_start % 1) * 1e9)

            intermediate_points.append(point)

        traj.points = intermediate_points
        goal = FollowJointTrajectory.Goal() 
        goal.trajectory = traj

        self._action_client.send_goal_async(goal)   
        self.current_positions = target

    def _look_down(self):
        self._move_to_target({
            "Neck_Pitch": 0.5,
            "Neck_Yaw": -0.6            
        })

    def _extend_forward(self):
        self._move_to_target(
            {
            "TorsoShoulder_Left_Pitch": -1.5,
            "ShoulderElbow_Left": 0.0
        })

    def _grab(self):
        if self._distance is None:
            self.get_logger().warn("No distance yet")
            return
        
        if self._distance is not 0.0 and self._distance <= 0.5:

            self._get_close()
            if self.pick_timer is not None:
                self.pick_timer.cancel()

            self.pick_timer = self.create_timer(9.0, self._pick_up)
            
        else:
            self.get_logger().warn("Too Far")

    def _get_close(self):
        self._send_trajectory([
            ({"ShoulderElbow_Left": -0.4363325,}, 0.5),
            ({"ShoulderElbow_Left": -0.872665,}, 0.5),
            ({"ShoulderElbow_Left": -1.35,}, 0.5),
            ({"ShoulderElbow_Left": -1.7,}, 0.5),

            ({"TorsoShoulder_Left_Pitch": -0.5,}, 0.5),            

            ({"ShoulderElbow_Left": -1.15,}, 0.5),

        ])

    def _pick_up(self):
        self._grasped = True
            
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
        
        self.pick_timer.cancel()
        self.pick_timer = None

    def _update_grab(self):
        if not self._grasped:
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
        req.state.pose.position.z = zp - offset

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
        self._grasped = False

    def _send_trajectory(self, keyframes):
        traj = JointTrajectory()
        traj.joint_names = ALL_JOINTS

        cumulative_time = 0.0

        for joint_dict, duration in keyframes:
            cumulative_time += duration

            point = JointTrajectoryPoint()

            positions = list(self.current_positions)

            for joint, value in joint_dict.items():
                if joint in traj.joint_names:
                    idx = traj.joint_names.index(joint)
                    positions[idx] = value

            point.positions = positions
            point.time_from_start.sec = int(cumulative_time)
            point.time_from_start.nanosec = int((cumulative_time % 1) * 1e9)

            traj.points.append(point)
            self.current_positions = positions

        goal = FollowJointTrajectory.Goal()
        goal.trajectory = traj

        self._action_client.send_goal_async(goal)

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