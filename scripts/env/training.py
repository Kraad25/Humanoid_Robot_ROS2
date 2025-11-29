import rclpy

from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from HumanoidRobotEnv import HumanoidRobotEnv

if __name__ == '__main__':
    rclpy.init()
    # check_env(HumanoidRobotEnv(render_mode=None, maxStep=1))

    env = HumanoidRobotEnv(render_mode=None, maxStep=1024, training=True)
    
    try:
        model = PPO.load("ppo_balancing", env=env)
        print("Loaded existing model")
    except:
        model = PPO("MlpPolicy", env)
        print("Training new model")

    model.learn(total_timesteps=50000, progress_bar=True)
    model.save("ppo_balancing")

    env.close()
