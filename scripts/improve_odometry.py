#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from gazebo_msgs.msg import ModelStates
from rclpy.qos import QoSProfile


class OdomGroundTruthPublisher(Node):
    def __init__(self):
        super().__init__("improve_odometry")

        self.declare_parameter('robot_name', 'walter')
        self.robot_name = self.get_parameter('robot_name').value  

        qos_profile = QoSProfile(depth=10)
        #! Odom_groundtruth is used in the parameter of social_nav_benchmark: controllers.yaml, mapping.yaml, planner.yaml
        self.odom_pub = self.create_publisher(Odometry, '/odom_groundtruth', 10)

        self.gazebo_sub = self.create_subscription(
            ModelStates, "/gazebo_spawner/model_states", self.send_odometry, qos_profile)

        self.get_logger().info("Improve odometry has been started")


    def send_odometry(self, msg: ModelStates):  
        try:
            
            index = msg.name.index(self.robot_name)

            
            pose = msg.pose[index]
            twist = msg.twist[index]
            odom_msg = Odometry()
            odom_msg.header.stamp = self.get_clock().now().to_msg()
            odom_msg.header.frame_id = "map"
            odom_msg.child_frame_id = "base_footprint"
            odom_msg.pose.pose.position = pose.position
            odom_msg.pose.pose.orientation = pose.orientation
            odom_msg.twist.twist.linear = twist.linear
            odom_msg.twist.twist.angular = twist.angular
            self.odom_pub.publish(odom_msg)
            
        except ValueError:
            self.get_logger().warn(f"Modelo {self.robot_name} no encontrado en Gazebo")


def main(args=None):
    rclpy.init(args=args)
    node = OdomGroundTruthPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
