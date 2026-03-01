ALL_JOINTS =  ["Neck_Yaw", "Neck_Pitch", "TorsoShoulder_Left_Pitch", "TorsoShoulder_Left_Roll",
                "ShoulderElbow_Left", "TorsoShoulder_Right_Pitch", "TorsoShoulder_Right_Roll",
                "ShoulderElbow_Right", "TorsoThigh_Left_Pitch", "TorsoThigh_Left_Yaw",
                "ThighCalf_Left", "CalfFoot_Left", "TorsoThigh_Right_Pitch",
                "TorsoThigh_Right_Yaw", "ThighCalf_Right", "CalfFoot_Right"
            ]

DEFAULT_JOINT_POSITION_VALUES = [
    0.0,   # Neck_Yaw
    0.0,   # Neck_Pitch
    
    0.1,   # TorsoShoulder_Left_Pitch (arms slightly forward)
    0.0,   # TorsoShoulder_Left_Roll
    0.0,   # ShoulderElbow_Left

    0.1,   # TorsoShoulder_Right_Pitch
    0.0,   # TorsoShoulder_Right_Roll
    0.0,   # ShoulderElbow_Right

    0.0,  # TorsoThigh_Left_Pitch (hip slightly flexed forward)
    0.0,   # TorsoThigh_Left_Yaw
    0.0,   # ThighCalf_Left (knee bent ~23°)
    0.0,  # CalfFoot_Left (ankle pitched back to keep foot flat)

    0.0,  # TorsoThigh_Right_Pitch
    0.0,   # TorsoThigh_Right_Yaw
    0.0,   # ThighCalf_Right
    0.0   # CalfFoot_Right
]

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
    "ThighCalf_Left": (-0.523599, 1.74533),           # (-30°, 100°)
    "CalfFoot_Left": (-0.785398, 0.785398),           # (-45°, 45°)
    "TorsoThigh_Right_Yaw": (-0.0872665, 0.349066),   # (-5°, 20°)
    "TorsoThigh_Right_Pitch": (-2.0944, 0.349066),    # (-120°, 20°)
    "ThighCalf_Right": (-0.523599, 1.74533),          # (-30°, 100°)
    "CalfFoot_Right": (-0.785398, 0.785398),          # (-45°, 45°)
}