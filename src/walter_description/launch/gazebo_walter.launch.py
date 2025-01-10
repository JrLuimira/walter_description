import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    # Nombre del paquete y archivo Xacro
    package_name = "walter_description"
    xacro_file = os.path.join(
        get_package_share_directory(package_name), "urdf", "robot.xacro"
    )

    # Procesar el archivo Xacro para obtener la descripción del robot
    robot_description_config = xacro.process_file(xacro_file).toxml()

    # Nodo robot_state_publisher
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher_node",
        parameters=[
            {"use_sim_time": True, "robot_description": robot_description_config}
        ],
        output="screen",
    )

    # Incluir el launch de Gazebo desde el paquete `gazebo_ros`
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("gazebo_ros"), "launch", "gazebo.launch.py"
            )
        ),
        launch_arguments={
            "verbose": "true",
        }.items(),
    )

    # Nodo para spawn_entity (añadir el robot a la simulación)
    spawn_entity_node = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-topic",
            "robot_description",
            "-entity",
            "walter",
            "-x",
            "0",
            "-y",
            "0",
            "-z",
            "0.1",  # Ajustar la posición inicial si es necesario
        ],
        output="screen",
    )

    # Añadir un retraso para asegurarse de que Gazebo está listo
    # spawn_entity_timer = TimerAction(
    #     period=5.0,  # 5 segundos de retraso
    #     actions=[spawn_entity_node]
    # )

    joint_state_publisher_node = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher_node",
        parameters=[{"use_sim_time": True}],
        output="screen",
    )
    # joint_state_publisher_timer = TimerAction(
    #     period=6.0,
    #     actions=[joint_state_publisher_node]
    # )

    # Descripción del lanzamiento
    return LaunchDescription(
        [
            gazebo_launch,
            robot_state_publisher_node,
            spawn_entity_node,
            joint_state_publisher_node,
            # spawn_entity_timer,
            # joint_state_publisher_timer,
        ]
    )
