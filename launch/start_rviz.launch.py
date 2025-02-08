import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():
    # Nombre del paquete
    package_description = "walter_description"
    walter_description_dir = FindPackageShare(package="walter_description").find(
        "walter_description"
    )

    # Nodo RViz2
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", walter_description_dir + "/rviz/walter.rviz"],
    )

    # Descripción del lanzamiento
    return LaunchDescription([
        rviz_node,
    ])