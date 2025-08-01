import gymnasium as gym
from gymnasium import spaces
from gymnasium.utils import EzPickle

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

from data import *
from contact_detector import ContactDetector
from Robot import Robot
import time

class HumanoidRobotEnv(gym.Env, Node):
    def __init__(self, render_mode=None, maxStep=None, training=True):
        EzPickle.__init__(self, render_mode)
        Node.__init__(self, "humanoid_robot_env")

        self.render_mode = render_mode
        self.maxStep = maxStep
        self.training = training

        # Training Variables
        self.current_step = 0
        self.tilt = None
        self.tilt_rate = None
        self.left_foot_contact = False
        self.right_foot_contact = False

        # Action and Observation Space
        self.action_space = spaces.Box(Action['low'], Action['high'])
        self.observation_space = spaces.Box(Observation['low'], Observation['high'])

        # Object Creation
        self.contact_detector = ContactDetector(self)
        self.robot = Robot(self, self.training)

        # Subscriptions
        self.imu_subscription = self.create_subscription(Imu, '/cleaned_imu', self._callback, 10)

    def reset(self, seed=None):
        self.contact_detector.set_enable_detection(False)

        self.robot.reset_pose()
        self._reset_episode_variables()
        self._ensure_imu_ready()

        self.contact_detector.set_enable_detection(True)

        return np.array(self._get_state(), dtype=np.float32), {}

    def step(self, action):
        self.current_step += 1

        self.robot.apply_action(action)
        rclpy.spin_once(self, timeout_sec=0.01)

        state = self._get_state()
        reward = self._compute_reward()
        terminated, truncated = self._check_termination()

        return np.array(state, dtype=np.float32), float(reward), terminated, truncated, {}

    def render(self):
        pass

    def close(self):
        self.destroy_node()
        rclpy.shutdown()

    def _callback(self, msg):
        self.tilt = msg.orientation.y
        self.tilt_rate = msg.angular_velocity.y

    def _get_state(self):
        state = [
            # IMU Orientation and Angular Velocity
            self.tilt,
            self.tilt_rate,

            # Joint Positions
            *self.robot.get_joint_positions(), # Unpacking joint positions list

            # Foot Contacts
            1.0 if self.left_foot_contact else 0.0,
            1.0 if self.right_foot_contact else 0.0
        ]

        return state
    
    def _reset_episode_variables(self):
        self.current_step = 0
        self.tilt = None
        self.tilt_rate = None
        self.left_foot_contact = False
        self.right_foot_contact = False

        self.contact_detector.reset()

    def _compute_reward(self):
        reward = 0.0

        if self.contact_detector.has_fallen():
            reward = -10.0
        if self.current_step >= self.maxStep:
            reward += 10.0

        reward += 1.0 # Survival reward

        return reward
    
    def _check_termination(self):
        terminated = self.contact_detector.has_fallen()
        truncated = self.current_step >= self.maxStep

        return terminated, truncated
    
    def _ensure_imu_ready(self, timeout_sec=5.0):
        # To prevent the imu values being None in _get_state() we wait to get the value after resetting it.
        deadline  = time.time() + timeout_sec
        while (self.tilt is None or self.tilt_rate is None) and time.time() < deadline:
            rclpy.spin_once(self, timeout_sec=0.1)
            
        if self.tilt is None or self.tilt_rate is None:
            self.get_logger().warn("Timeout waiting for IMU data.")