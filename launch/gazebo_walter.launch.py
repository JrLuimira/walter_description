import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():

    # Obtener directorios de paquetes
    walter_description_dir = FindPackageShare(package="walter_description").find(
        "walter_description"
    )
    
    turtlebot3_gazebo_dir = FindPackageShare(package="turtlebot3_gazebo").find(
        "turtlebot3_gazebo"
    )
    gazebo_ros_dir = FindPackageShare(package="gazebo_ros").find("gazebo_ros")

    # Ruta del archivo SDF del mundo
    # world_file = PathJoinSubstitution(
    #     [walter_description_dir, "worlds", "muestra", "model.sdf"]
    # )

    world_file = PathJoinSubstitution(
        [walter_description_dir, "worlds", "turtlebot3_house.world"]
    )

    # Declarar argumento de mundo
    declare_world_arg = DeclareLaunchArgument(
        "world", default_value=world_file, description="World file"
    )

    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation time or not.",
        choices=["true", "false"],
    )

    # Incluir el launch de Gazebo con el mundo definido
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([gazebo_ros_dir, "launch", "gazebo.launch.py"])
        ),
        launch_arguments={
            "world": LaunchConfiguration("world"),
        }.items(),
    )

    # Incluir el launch para spawnear el robot
    spawn_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [walter_description_dir, "launch", "walter_spawn.launch.py"]
            )
        ),
        launch_arguments={"y": "0"}.items(),
    )

    # Nodo para publicar el estado del robot
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[
            {
                "use_sim_time": LaunchConfiguration("use_sim_time"),
                "robot_description": Command(
                    [
                        "xacro ",
                        PathJoinSubstitution(
                            [walter_description_dir, "urdf", "walter.xacro"]
                        ),
                    ]
                ),
            }
        ],
    )

    # Definir la descripción del lanzamiento
    ld = LaunchDescription()

    # Agregar argumento de mundo
    ld.add_action(declare_world_arg)
    ld.add_action(declare_use_sim_time)

    # Agregar nodos y lanzamientos
    ld.add_action(robot_state_publisher_node)
    ld.add_action(gazebo_launch)
    ld.add_action(spawn_launch)

    return ld
