#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from tf2_ros import (
    TransformBroadcaster,
    TransformListener,
    Buffer,
)
from geometry_msgs.msg import TransformStamped
from gazebo_msgs.msg import ModelStates
from rclpy.qos import QoSProfile
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import Odometry


class GroundTruthBroadcaster(Node):
    def __init__(self):
        super().__init__("groundtruth_broadcaster")

        self.declare_parameter("init_pose_x", 0)
        self.declare_parameter("init_pose_y", 0)

        self.init_pose_x = self.get_parameter("init_pose_x").value
        self.init_pose_y = self.get_parameter("init_pose_y").value

        #! This is for odom -- base_footprint
        self.br = TransformBroadcaster(self)
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)

        qos_profile = QoSProfile(depth=10)
        self.models_pose_sub = self.create_subscription(
            ModelStates, "/gazebo_spawner/model_states", self.model_pose_cb, qos_profile
        )

        self.tf_sub = self.create_subscription(
            TFMessage, "/tf", self.tf_cb, qos_profile
        )

        self.chassis_position = [0.0, 0.0, 0.0]
        self.chassis_orientation = [0.0, 0.0, 0.0, 1.0]


        #! TIMEERS
        self.timer = self.create_timer(0.01, self.send_transforms)
        self.stamp = 0


    def tf_cb(self, msg: TFMessage):
        self.stamp = msg.transforms[0].header.stamp

    def model_pose_cb(self, msg: ModelStates):
        models_list = msg.name
        models_pose = msg.pose

        try:
            chassis_index = models_list.index("walter")

            walter_position = models_pose[chassis_index].position
            walter_orientation = models_pose[chassis_index].orientation

            self.chassis_position = [
                walter_position.x - self.init_pose_x,
                walter_position.y - self.init_pose_y,
                0.0,
            ]
            self.chassis_orientation = [
                walter_orientation.x,
                walter_orientation.y,
                walter_orientation.z,
                walter_orientation.w,
            ]
        except ValueError:
            pass
    

    def odom_cb(self, msg: Odometry):
        self.stamp2 = msg.header.stamp
        self.chassis_position = [
            msg.pose.pose.position.x - self.init_pose_x,
            msg.pose.pose.position.y - self.init_pose_y,
            0.0,
        ]
        self.chassis_orientation = [
            msg.pose.pose.orientation.x,
            msg.pose.pose.orientation.y,
            msg.pose.pose.orientation.z,
            msg.pose.pose.orientation.w,
        ]

    def send_transforms(self):
        if self.stamp != 0:
            self.send_transform(
                self.chassis_position, self.chassis_orientation, "base_footprint"
            )

    def send_transform(self, position, orientation, child_frame_id):
        t = TransformStamped()
        t.header.stamp = self.stamp
        t.header.frame_id = "odom"
        t.child_frame_id = child_frame_id
        t.transform.translation.x = position[0]
        t.transform.translation.y = position[1]
        t.transform.translation.z = position[2]
        t.transform.rotation.x = orientation[0]
        t.transform.rotation.y = orientation[1]
        t.transform.rotation.z = orientation[2]
        t.transform.rotation.w = orientation[3]

        self.br.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    tf_broadcaster = GroundTruthBroadcaster()
    rclpy.spin(tf_broadcaster)

    tf_broadcaster.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
