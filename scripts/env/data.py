import numpy as np
import math


# Action Space
Action = {
    # Motor speed percentage and Direction for all joints of the humanoid robot.
    # For, Neck Yaw, Neck Pitch,
    # Left Shoulder Pitch, Left Shoulder Roll, Left Elbow Pitch,
    # Right Shoulder Pitch, Right Shoulder Roll, Right Elbow Pitch,
    # Left Hip Pitch, Left Hip Yaw, Left Knee Pitch, Left Foot Pitch.
    # Right Hip Pitch, Right Hip Yaw, Right Knee Pitch, Right Foot Pitch,
    # Total 16 joints, each joint can be controlled with a value between -1 and 1
    # where -1 is full speed in one direction and 1 is full speed in the opposite direction.
    
    "low": np.array([-1]*16).astype(np.float32), 
    "high": np.array([1]*16).astype(np.float32)
}

# Observation Space
Observation = {
    # Imu's orientation and angular velocity, all 16 joints's position and 2 more values for foot contacts.
    "low": np.array([-math.pi, -2] + [-1]*16 + [0.0, 0.0]).astype(np.float32),
    "high": np.array([math.pi, 2] + [1]*16 + [1.0, 1.0]).astype(np.float32)
}

ALL_JOINTS =  ["Neck_Yaw", "Neck_Pitch", "TorsoShoulder_Left_Pitch", "TorsoShoulder_Left_Roll",
                "ShoulderElbow_Left", "TorsoShoulder_Right_Pitch", "TorsoShoulder_Right_Roll",
                "ShoulderElbow_Right", "TorsoThigh_Left_Pitch", "TorsoThigh_Left_Yaw",
                "ThighCalf_Left", "CalfFoot_Left", "TorsoThigh_Right_Pitch",
                "TorsoThigh_Right_Yaw", "ThighCalf_Right", "CalfFoot_Right"
            ]

DEFAULT_JOINT_POSITION_VALUES = [0.0] * len(ALL_JOINTS)

JOINT_LIMITS = {
    "Neck_Yaw": (-1.0472, 1.0472),                    # (-60°, 60°)
    "Neck_Pitch": (-0.523599, 0.523599),              # (-30°, 30°)
    "TorsoShoulder_Left_Roll": (-1.0472, 0.0),        # (-60°, 0°)
    "TorsoShoulder_Left_Pitch": (-3.14159, 0.349066), # (-180°, 20°)
    "ShoulderElbow_Left": (-1.74533, 0.349066),       # (-100°, 20°)
    "TorsoShoulder_Right_Roll": (0.0, 1.0472),        # (0°, 60°)
    "TorsoShoulder_Right_Pitch": (-3.14159, 0.349066),# (-180°, 20°)
    "ShoulderElbow_Right": (-1.74533, 0.349066),      # (-100°, 20°)
    "TorsoThigh_Left_Yaw": (-0.0872665, 0.349066),    # (-5°, 20°)
    "TorsoThigh_Left_Pitch": (-2.0944, 0.349066),     # (-120°, 20°)
    "ThighCalf_Left": (-0.349066, 1.74533),           # (-20°, 100°)
    "CalfFoot_Left": (-0.785398, 0.785398),           # (-45°, 45°)
    "TorsoThigh_Right_Yaw": (-0.0872665, 0.349066),   # (-5°, 20°)
    "TorsoThigh_Right_Pitch": (-2.0944, 0.349066),    # (-120°, 20°)
    "ThighCalf_Right": (-0.349066, 1.74533),          # (-20°, 100°)
    "CalfFoot_Right": (-0.785398, 0.785398),          # (-45°, 45°)
}
