#include <functional>
#include <vector>

#include <gazebo/common/Plugin.hh>
#include <gazebo/common/Events.hh>

#include <gazebo/physics/Model.hh>
#include <gazebo/physics/Joint.hh>
#include <gazebo/physics/Link.hh>
#include <gazebo/physics/Inertial.hh>
#include <gazebo/physics/World.hh>  

#include <ignition/math/Pose3.hh>

namespace gazebo
{
  class FixedBaseSupportPlugin : public ModelPlugin
  {
  public:
    void Load(physics::ModelPtr model, sdf::ElementPtr)
    {
      std::cout << "[FixedBaseSupportPlugin] Loaded" << std::endl;

      this->model = model;
      this->base_link = model->GetLink("base_link");
      if (!this->base_link)
      {
        std::cerr << "Base link not found!" << std::endl;
        return;
      }

      base_link->SetKinematic(true);
      base_link->SetGravityMode(false);

      model->SetWorldPose(
        ignition::math::Pose3d(0, 0, 0.02, 0, 0, 0)
      );

      
      this->ankle_left  = model->GetJoint("CalfFoot_Left");
      this->ankle_right = model->GetJoint("CalfFoot_Right");

      if (!ankle_left || !ankle_right)
      {
        std::cerr << "Ankle joints not found!" << std::endl;
      }
      this->updateConnection =
        event::Events::ConnectWorldUpdateBegin(
          std::bind(&FixedBaseSupportPlugin::OnUpdate, this));
    }

    void OnUpdate()
    {
      const double ankle_angle = -0.0;

      auto lock_ankle = [&](physics::JointPtr ankle)
      {
        if (!ankle) return;

        if (std::abs(ankle->Position(0) - ankle_angle) > 1e-6)
        {
          ankle->SetPosition(0, ankle_angle);
        }
        ankle->SetVelocity(0, 0.0);
        ankle->SetForce(0, 0.0);
      };

      lock_ankle(ankle_left);
      lock_ankle(ankle_right);
    }

  private:
    physics::ModelPtr model;
    physics::LinkPtr base_link;
    physics::JointPtr ankle_left;
    physics::JointPtr ankle_right;

    event::ConnectionPtr updateConnection;

    double total_mass;

  };

  GZ_REGISTER_MODEL_PLUGIN(FixedBaseSupportPlugin)
}