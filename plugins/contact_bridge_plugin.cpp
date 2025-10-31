#include <gazebo/common/Plugin.hh>
#include <gazebo/sensors/Sensor.hh>
#include <gazebo/sensors/ContactSensor.hh>
#include <gazebo/sensors/SensorManager.hh>
#include <gazebo/transport/transport.hh>
#include <gazebo/msgs/msgs.hh>
#include <gazebo/msgs/contacts.pb.h>
#include <gazebo/physics/World.hh>

#include <gazebo_ros/node.hpp>
#include <rclcpp/rclcpp.hpp>

#include "humanoid_robot/msg/contacts.hpp"
#include "humanoid_robot/msg/contact.hpp"  

namespace gazebo{
    class ContactBridgePlugin  : public WorldPlugin{
        public: 

            ContactBridgePlugin () : WorldPlugin() {} // Call WorldPlugin Constructor

            void Load(physics::WorldPtr _world, sdf::ElementPtr _sdf) override
            {
                // Initialize ROS 2 node for plugin and setup publisher
                this->ros_node_ = gazebo_ros::Node::Get(_sdf);
                this->pub_ = this->ros_node_->create_publisher<humanoid_robot::msg::Contacts>("contacts", 10);

                // Setup Gazebo transport
                this->gz_node_ = transport::NodePtr(new transport::Node());
                this->gz_node_->Init(_world->Name());
                this->contact_sub_ = this->gz_node_->Subscribe("~/physics/contacts",
                                    &ContactBridgePlugin ::OnContacts, this);

                RCLCPP_INFO(rclcpp::get_logger("ContactBridgePlugin"), "Subscribed to Gazebo contacts");
            }

        private:
            void OnContacts(ConstContactsPtr &gz_msg){
                humanoid_robot::msg::Contacts ros_msg;
                ros_msg.header.stamp = this->ros_node_->now();

                for (int i = 0; i < gz_msg->contact_size(); ++i){
                    const auto &contact = gz_msg->contact(i);

                    humanoid_robot::msg::Contact contact_msg;
                    contact_msg.info = contact.DebugString();
                    ros_msg.states.push_back(contact_msg);
                }

                if (!ros_msg.states.empty()){
                    this->pub_->publish(ros_msg);
                }
            }

        private:
            gazebo_ros::Node::SharedPtr ros_node_;
            rclcpp::Publisher<humanoid_robot::msg::Contacts>::SharedPtr pub_;

            transport::NodePtr gz_node_;
            transport::SubscriberPtr contact_sub_;
        };

    GZ_REGISTER_WORLD_PLUGIN(ContactBridgePlugin)

}