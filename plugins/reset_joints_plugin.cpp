#include <gazebo/common/Plugin.hh>
#include <gazebo/physics/physics.hh>

#include <gazebo_ros/node.hpp>
#include <rclcpp/rclcpp.hpp>

#include "humanoid_robot/srv/reset_joints.hpp"

namespace gazebo{
  class ResetJointsPlugin : public gazebo::WorldPlugin{
      public:
        void Load(physics::WorldPtr world, sdf::ElementPtr _sdf) override
        {
          this->world_ = world;
          this->ros_node_ = gazebo_ros::Node::Get(_sdf);

          this->service_ = this->ros_node_->create_service<humanoid_robot::srv::ResetJoints>(
            "/reset_joints",
            std::bind(&ResetJointsPlugin::OnReset, this,
                      std::placeholders::_1, std::placeholders::_2));
        }

      private:
        void OnReset(const std::shared_ptr<humanoid_robot::srv::ResetJoints::Request> req,
                    std::shared_ptr<humanoid_robot::srv::ResetJoints::Response> res)
        {
          auto model = this->world_->ModelByName("Selene");  // your robot name
          if (!model) {
            RCLCPP_ERROR(this->ros_node_->get_logger(), "Model Selene not found!");
            res->success = false;
            return;
          }

          for (size_t i = 0; i < req->joint_names.size(); i++)
          {
            auto joint = model->GetJoint(req->joint_names[i]);
            if (joint)
            {
              joint->SetPosition(0, req->positions[i]);  // instant snap
            }
            else
            {
              RCLCPP_WARN(this->ros_node_->get_logger(),
                          "Joint %s not found", req->joint_names[i].c_str());
            }
          }

          res->success = true;
        }

      private:
        gazebo_ros::Node::SharedPtr ros_node_;
        physics::WorldPtr world_;
        rclcpp::Service<humanoid_robot::srv::ResetJoints>::SharedPtr service_;
      };

  GZ_REGISTER_WORLD_PLUGIN(ResetJointsPlugin)

}

