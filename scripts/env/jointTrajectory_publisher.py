from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from data import ALL_JOINTS, DEFAULT_JOINT_POSITION_VALUES

class JointTrajectoryPub:
    def __init__(self, env):
        self.env = env
        self.publisher = self.env.create_publisher(JointTrajectory, '/joint_trajectory_controller/joint_trajectory', 10)

    def publish_trajectory(self, trajectory_msg):
        self.publisher.publish(trajectory_msg)

    def set_target_trajectory(self, joint_name, value, time_to_end_sec=1):
        trajectory_msg = JointTrajectory()
        trajectory_msg.joint_names = ALL_JOINTS
        
        trajectory_msg.points.append(JointTrajectoryPoint())
        trajectory_msg.points[0].positions = DEFAULT_JOINT_POSITION_VALUES

        for i in range(len(joint_name)):
            if joint_name[i] in trajectory_msg.joint_names:
                index = trajectory_msg.joint_names.index(joint_name[i])
                trajectory_msg.points[0].positions[index] = value[i]
                
        secs = int(time_to_end_sec)
        nsecs = int((time_to_end_sec - secs) * 1e9)

        trajectory_msg.points[0].time_from_start.sec = secs
        trajectory_msg.points[0].time_from_start.nanosec = nsecs

        self.publish_trajectory(trajectory_msg)
