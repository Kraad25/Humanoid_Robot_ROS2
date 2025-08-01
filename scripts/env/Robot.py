from gazebo_msgs.srv import SetEntityState
from gazebo_msgs.msg import EntityState
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState
import rclpy

from tf_transformations import quaternion_from_euler
from data import *
from jointTrajectory_publisher import JointTrajectoryPub

class Robot:    
    def __init__(self, env, training=True):
        self.training = training
        self.env = env

        self.joints = ALL_JOINTS
        self.default_joint_positions = DEFAULT_JOINT_POSITION_VALUES
        self.current_joint_state = None

        self.trajectory_node = JointTrajectoryPub(self.env)

        self.jointState_sub = self.env.create_subscription(JointState, '/cleaned_jointState', self._callback, 10)

    def reset_pose(self):
        client = self._get_entity_client()
        request = self._create_reset_request()
        self._send_request(client, request)

    def apply_action(self, action):
        mapped_actions = self._map_action_to_angle(action)
        self.trajectory_node.set_target_trajectory(self.joints, mapped_actions)

    def get_joint_positions(self):
        if self.current_joint_state:
            return self.current_joint_state.position     
        return self.default_joint_positions

    def _callback(self, msg):
        self.current_joint_state = msg

    def _get_entity_client(self):
        client = self.env.create_client(SetEntityState, '/set_entity_state')
        while not client.wait_for_service(timeout_sec=1.0):
            self.env.get_logger().warn("Waiting for /set_entity_state service...")

        return client
    
    def _create_reset_request(self):
        request = SetEntityState.Request()
        request.state = EntityState()
        request.state.name = "Selene"

        self._set_pose(request.state) # Pose (Position and Orientation)
        self._set_twist(request.state) # Twist (Velocity)

        return request
    
    def _send_request(self, client, request):
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self.env, future)

        if future.result() is None:
            self.env.get_logger().error("Failed to reset robot pose.")

    def _set_pose(self, state):
        state.pose.position.x = 0.0
        state.pose.position.y = 0.0
        state.pose.position.z = 0.2 

        tilt = self._apply_random_tilt()
        q = quaternion_from_euler(0.0, tilt, 0.0)
        state.pose.orientation.x = q[0]
        state.pose.orientation.y = q[1]
        state.pose.orientation.z = q[2]
        state.pose.orientation.w = q[3]

    def _set_twist(self, state):
        state.twist.linear.x = 0.0
        state.twist.linear.y = 0.0
        state.twist.linear.z = 0.0
        state.twist.angular.x = 0.0
        state.twist.angular.y = 0.0
        state.twist.angular.z = 0.0

    def _apply_random_tilt(self):
        return 0.0
    
    def _map_action_to_angle(self, action):
        mapped_actions = []
        for i, joint_name in enumerate(self.joints):
            low, high = JOINT_LIMITS[joint_name]
            mapped_value = self._map(action[i], -1.0, 1.0, low, high)
            mapped_actions.append(mapped_value)
        return mapped_actions

    def _map(self, value, from_min, from_max, to_min, to_max):
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min
