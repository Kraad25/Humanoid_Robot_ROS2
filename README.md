# Humanoid_Robot_ROS2
This project simulates a Humanoid Robot, Developed with ROS2 Humble and Gazebo in Ubuntu.

## User Instruction
### Prerequisites:
 * Install ROS2 Humble [Installation Guide](https://docs.ros.org/en/humble/Installation.html) (if not already installed)
 * Install Gazebo by running,
    ```bash
    sudo apt update
    sudo apt install -y curl gnupg lsb-release
    curl -sSL http://repo.ros2.org/repos.key | sudo apt-key add -
    sudo sh -c 'echo "deb [arch=amd64] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2-latest.list'
    sudo apt update
    sudo apt install gazebo -y

### Installation and Setup:
 * Navigate to Your ROS2 Workspace.
 * Clone the Project:
    ```bash
    git clone https://github.com/Kraad25/Humanoid_Robot_ROS2.git [package_name]
 * Build the Workspace and source it.
 * Launch the Simulation.
