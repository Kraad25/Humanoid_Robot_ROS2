import rclpy
from stable_baselines3 import PPO
from HumanoidRobotEnv import HumanoidRobotEnv

# Test trained agent
def evaluate_model(model, env):
    done = False
    obs, _ = env.reset()
    while not done:
        action, _states = model.predict(obs)
        obs, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
        env.render()

if __name__ == "__main__":
    rclpy.init()
    env = HumanoidRobotEnv(training=False)
    try:
        model = PPO.load("ppo_balancing", env=env)
        print("Loaded existing model")
    except Exception as e:
        print("Train the model first")
        exit(1)

    evaluate_model(model, env)